from flask import Blueprint, jsonify
import os

config_bp = Blueprint('config', __name__)

@config_bp.route('/config/ports')
def get_ports():
    """获取应用的端口配置"""
    return jsonify({
        'status': 'success',
        'data': {
            'frontend': int(os.getenv('FRONTEND_PORT', '6060')),
            'gradio': int(os.getenv('GRADIO_PORT', '7070')),
            'langmanus_web': int(os.getenv('LANGMANUS_WEB_PORT', '3000')),
            'langmanus_api': int(os.getenv('LANGMANUS_API_PORT', '8000'))
        }
    }) 