from flask import jsonify
from werkzeug.http import HTTP_STATUS_CODES

def error_response(status_code, message=None):
    """生成错误响应"""
    payload = {'error': HTTP_STATUS_CODES.get(status_code, 'Unknown error')}
    if message:
        payload['message'] = message
    response = jsonify(payload)
    response.status_code = status_code
    return response

def bad_request(message):
    """400错误"""
    return error_response(400, message)

def unauthorized(message):
    """401错误"""
    return error_response(401, message)

def forbidden(message):
    """403错误"""
    return error_response(403, message)

def not_found(message):
    """404错误"""
    return error_response(404, message) 