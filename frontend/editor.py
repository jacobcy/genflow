import gradio as gr
from flask import request, Flask, render_template, render_template_string
from app.utils.security import verify_token
import os
import threading
import socket

# 编辑器HTML模板不再包含完整内容，仅保留引用
# 这个常量被保留以兼容当前__init__.py中的代码
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <title>简易文章编辑器</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='0.9em' font-size='90'>📝</text></svg>">
    <link href="https://fonts.googleapis.com/css2?family=Source+Code+Pro:wght@400;600&family=Source+Sans+Pro:wght@400;600&display=swap" rel="stylesheet">
    <link href="https://cdn.bootcdn.net/ajax/libs/twitter-bootstrap/5.3.1/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.bootcdn.net/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <link href="/static/css/editor/styles.css" rel="stylesheet">
    <style>
        body {
            font-family: 'Source Sans Pro', Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>简易文章编辑器</h1>
        </div>
        <div class="editor-container">
            <div class="editor">
                <textarea id="editor" placeholder="在此输入您的文章内容..."></textarea>
            </div>
            <div class="preview" id="preview">
                <!-- 预览内容将在这里显示 -->
                <p class="text-muted">在左侧输入文本后，预览将显示在这里</p>
            </div>
        </div>
        <div class="save-status" id="saveStatus"></div>
        <div class="toolbar">
            <button id="saveBtn" class="btn btn-success">保存文章</button>
            <button id="clearBtn" class="btn btn-danger">清空内容</button>
        </div>
    </div>

    <script>
        // 文章数据注入点 - 这里将会被app/__init__.py中的代码替换
        window.addEventListener('load', function() {
            // 初始化代码会在这里
        });
    </script>
    <script src="https://cdn.bootcdn.net/ajax/libs/bootstrap/5.3.1/js/bootstrap.bundle.min.js"></script>
    <script src="/static/js/editor/main.js"></script>
</body>
</html>
"""

# 恢复ArticleEditor类以保持向后兼容性
class ArticleEditor:
    """文章编辑器类，为保持兼容性而保留"""
    def __init__(self):
        """初始化编辑器实例"""
        # 使用环境变量中的端口
        self.gradio_port = int(os.getenv('GRADIO_PORT', '7070'))
        self.app = None
        
        # 启动Gradio增强编辑器
        gradio_thread = threading.Thread(target=self._run_gradio_editor)
        gradio_thread.daemon = True
        gradio_thread.start()
    
    def _run_gradio_editor(self):
        """运行Gradio增强编辑器（未来实现）"""
        try:
            # 从环境变量获取端口
            self.gradio_port = int(os.getenv('GRADIO_PORT', '7070'))
            
            print(f"\n=== Gradio增强编辑器 ===")
            print(f"预计将在端口 {self.gradio_port} 上运行")
            print("【注意】目前仅作为占位符，实际功能未实现")
            print(f"目前访问 http://localhost:{self.gradio_port}/ 将显示临时页面\n")
            
            # 创建临时Flask应用作为占位符
            placeholder_app = self._create_placeholder_app()
            
            # 使用环境变量中的主机和端口
            host = os.getenv('FLASK_HOST', 'localhost')
            placeholder_app.run(
                host=host,
                port=self.gradio_port,
                debug=False
            )
        except Exception as e:
            print(f"[ERROR] 启动Gradio增强编辑器失败: {str(e)}")
            
            # 当前工作目录、环境变量等信息
            try:
                print(f"当前工作目录: {os.getcwd()}")
                print(f"FLASK_APP: {os.getenv('FLASK_APP', '未设置')}")
                print(f"DEBUG模式: {os.getenv('FLASK_DEBUG', '未设置')}")
                
                # 尝试保存端口信息到临时文件
                try:
                    with open('temp_editor_port.txt', 'w') as f:
                        f.write(str(self.gradio_port))
                    print(f"编辑器端口已保存到临时文件")
                except Exception as e:
                    print(f"[WARNING] 无法保存编辑器端口信息: {str(e)}")
            except Exception as log_e:
                print(f"[ERROR] 无法记录调试信息: {str(log_e)}")
    
    def _create_placeholder_app(self):
        """创建临时占位页面"""
        app = Flask(__name__)
        
        @app.route('/')
        def index():
            placeholder_html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>增强编辑器（开发中）</title>
                <style>
                    body { font-family: Arial, sans-serif; text-align: center; margin-top: 100px; }
                    .container { max-width: 600px; margin: 0 auto; }
                    .badge { background-color: #f8d7da; color: #721c24; padding: 5px 10px; border-radius: 3px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>增强编辑器 <span class="badge">开发中</span></h1>
                    <p>Gradio增强编辑器功能正在开发中，敬请期待。</p>
                    <p>目前请使用主应用的<a href="/editor">简易编辑器</a>。</p>
                </div>
            </body>
            </html>
            """
            return placeholder_html
        
        return app

# 保持原有的verify_gradio_access函数以避免导入错误
def verify_gradio_access():
    """验证访问权限（保留但不再使用）"""
    token = request.headers.get('Authorization')
    if not token or not verify_token(token):
        raise ValueError("未授权访问")

def find_available_port(start_port, max_port=None):
    """查找可用端口"""
    if max_port is None:
        max_port = start_port + 10
    
    for port in range(start_port, max_port + 1):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    raise OSError(f"无法找到可用端口 (范围: {start_port}-{max_port})")

def get_gradio_app():
    """获取编辑器应用实例并启动服务"""
    # 创建ArticleEditor实例并返回
    return ArticleEditor()
