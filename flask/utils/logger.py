import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logger(app):
    """配置日志系统"""
    
    # 确保日志目录存在
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 创建日志文件处理器
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, 'genflow.log'),
        maxBytes=1024 * 1024,  # 1MB
        backupCount=10
    )
    
    # 设置日志格式
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )
    file_handler.setFormatter(formatter)
    
    # 设置日志级别
    file_handler.setLevel(logging.INFO)
    
    # 添加到应用
    app.logger.addHandler(file_handler)
    
    # 配置基础日志
    logging.basicConfig(level=logging.INFO)
    
    return app 