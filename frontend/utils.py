"""
前端工具函数模块
提供通用的工具函数和装饰器
"""

import functools
import gradio as gr
import markdown
import logging

logger = logging.getLogger(__name__)

def handle_api_error(func):
    """API 错误处理装饰器"""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except gr.Error as e:
            # Gradio 错误直接抛出
            raise
        except Exception as e:
            logger.error(f"API 调用错误: {str(e)}")
            raise gr.Error(f"操作失败: {str(e)}")
    return wrapper

def update_preview(title: str, content: str) -> str:
    """更新文章预览
    
    将 Markdown 格式的文章内容转换为 HTML 预览
    """
    try:
        html_content = markdown.markdown(content)
        return f"<h1>{title}</h1>\n{html_content}"
    except Exception as e:
        logger.error(f"预览更新失败: {str(e)}")
        return "<p>预览生成失败</p>"

def format_error_message(error: Exception) -> str:
    """格式化错误信息"""
    return f"错误: {str(error)}"

def validate_article_data(title: str, content: str) -> bool:
    """验证文章数据
    
    Args:
        title: 文章标题
        content: 文章内容
    
    Returns:
        bool: 数据是否有效
    """
    if not title or len(title.strip()) < 5:
        raise gr.Error("标题不能为空且长度需大于5个字符")
    
    if not content or len(content.strip()) < 100:
        raise gr.Error("文章内容不能为空且长度需大于100个字符")
    
    return True
