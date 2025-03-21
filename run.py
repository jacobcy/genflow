from dotenv import load_dotenv
load_dotenv()  # 确保最早加载环境变量

import click
from app import create_app
import os
import subprocess
import sys
import webbrowser
from threading import Timer
import time
import signal
import atexit

def cleanup_resources():
    """清理资源"""
    cleanup_processes()

def signal_handler(sig, frame):
    """信号处理函数"""
    print('正在关闭应用...')
    os._exit(0)

def cleanup_processes():
    """清理已运行的进程，采用更安全的方式"""
    flask_port = os.getenv('FRONTEND_PORT', '6060')
    
    try:
        if sys.platform == 'win32':
            # 只清理特定端口上的 Python 进程
            subprocess.run(f'netstat -ano | findstr :{flask_port} | findstr LISTENING', shell=True, stderr=subprocess.DEVNULL)
        else:
            # 使用更温和的方式清理端口
            subprocess.run(f"lsof -t -i:{flask_port} | xargs -r kill", shell=True, stderr=subprocess.DEVNULL)
            time.sleep(1)  # 等待进程清理
            subprocess.run(f"lsof -t -i:{flask_port} | xargs -r kill -9", shell=True, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"清理进程时发生错误: {e}")
        pass

def open_browser(url):
    """在新线程中打开浏览器"""
    webbrowser.open(url)

def check_and_clean_port(port, description=""):
    """检查端口是否被占用，如果被占用则尝试清理"""
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            if sys.platform == 'win32':
                # Windows 下检查端口
                result = subprocess.run(f'netstat -ano | findstr :{port}', 
                                     shell=True, capture_output=True, text=True)
                if result.stdout.strip():
                    click.echo(f"{description} 端口 {port} 已被占用，正在清理... (尝试 {attempt + 1}/{max_attempts})")
                    # 获取进程 ID
                    for line in result.stdout.splitlines():
                        if f":{port}" in line:
                            pid = line.split()[-1]
                            subprocess.run(f'taskkill /F /PID {pid}', shell=True, stderr=subprocess.DEVNULL)
            else:
                # Unix 系统下检查端口
                result = subprocess.run(f'lsof -i:{port}', shell=True, capture_output=True, text=True)
                if result.stdout.strip():
                    click.echo(f"{description} 端口 {port} 已被占用，正在清理... (尝试 {attempt + 1}/{max_attempts})")
                    subprocess.run(f"lsof -t -i:{port} | xargs -r kill", shell=True, stderr=subprocess.DEVNULL)
            
            # 验证端口是否已经被清理
            time.sleep(1)  # 等待进程完全终止
            verify_cmd = 'netstat -ano' if sys.platform == 'win32' else f'lsof -i:{port}'
            verify_result = subprocess.run(verify_cmd, shell=True, capture_output=True, text=True)
            if f":{port}" not in verify_result.stdout:
                click.echo(f"{description} 端口 {port} 已成功清理")
                return True
            
        except Exception as e:
            click.echo(f"清理端口 {port} 时发生错误: {e}")
        
        if attempt < max_attempts - 1:
            time.sleep(2)  # 在重试之前等待
    
    click.echo(f"警告: 无法完全清理 {description} 端口 {port}，请手动检查")
    return False

@click.command()
@click.option('--env', default='development', 
              type=click.Choice(['development', 'production']), 
              help='运行环境: development 或 production')
@click.option('--host', default=os.getenv('FLASK_HOST', 'localhost'), help='主机地址')
@click.option('--port', default=int(os.getenv('FRONTEND_PORT', '6060')), help='端口号')
@click.option('--no-browser', is_flag=True, help='不自动打开浏览器')
def run(env, host, port, no_browser):
    """启动 GenFlow 应用"""
    # 设置环境变量
    os.environ['FLASK_ENV'] = env
    os.environ['FRONTEND_PORT'] = str(port)
    os.environ['FLASK_RUN_PORT'] = str(port)
    
    print(f"\n=== 正在 {env} 环境中启动 GenFlow ===\n")
    
    # 检查并清理主应用端口
    if not check_and_clean_port(port, "Flask"):
        click.echo(f"错误: 无法清理 Flask 端口 {port}，程序退出")
        return
    
    # 创建应用实例
    app = create_app(env)
    
    # 计算 worker 数量（减少开发环境的 worker 数量）
    workers = os.cpu_count() if env == 'production' else 1
    
    # 配置 gunicorn
    cmd = [
        'gunicorn',
        '--bind', f'{host}:{port}',
        '--workers', str(workers),
        '--worker-class', 'sync',
        '--max-requests', '1000',
        '--max-requests-jitter', '50',
        '--timeout', '120',
        '--graceful-timeout', '30',
        '--keep-alive', '5',
        '--log-level', 'info',
        '--reload' if env == 'development' else '',
        '--env', f'FLASK_APP=wsgi:application',
        '--env', f'FRONTEND_PORT={port}',
        '--env', f'FLASK_RUN_PORT={port}',
        'wsgi:application'
    ]
    
    # 开发环境自动打开浏览器
    if env == 'development' and not no_browser:
        Timer(2, open_browser, args=[f'http://{host}:{port}']).start()
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 注册清理函数
    atexit.register(cleanup_resources)
    
    # 启动 gunicorn
    subprocess.run(' '.join(filter(None, cmd)), shell=True)

if __name__ == '__main__':
    run() 