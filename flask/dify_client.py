import requests
import json
import os
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class DifyClient:
    """与Dify API交互的客户端类"""
    
    def __init__(self):
        """初始化Dify客户端"""
        # Dify API配置
        self.api_key = os.getenv('DIFY_API_KEY', '')
        self.api_url = os.getenv('DIFY_API_URL', 'https://api.dify.ai/v1')
        self.app_id = os.getenv('DIFY_APP_ID', '')
        
        # 检查配置是否完整
        if not all([self.api_key, self.api_url, self.app_id]):
            logging.warning("Dify配置不完整，部分功能可能不可用")
    
    def _make_request(self, endpoint, method="POST", data=None, files=None):
        """发送请求到Dify API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        url = f"{self.api_url}/{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers)
            elif method == "POST":
                if files:
                    response = requests.post(url, headers=headers, data=data, files=files)
                else:
                    headers["Content-Type"] = "application/json"
                    response = requests.post(url, headers=headers, data=json.dumps(data))
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")
            
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"Dify API请求错误: {str(e)}")
            return {"error": str(e)}
    
    def get_suggestion(self, title, content, suggestion_type="content"):
        """获取AI内容建议
        
        参数:
            title (str): 文章标题
            content (str): 文章内容
            suggestion_type (str): 建议类型，可选值: 'title', 'content', 'seo'
        
        返回:
            dict: 包含AI建议的响应
        """
        # 根据建议类型构建不同的提示
        prompts = {
            "title": f"请为以下内容提供5个更吸引人的标题建议:\n\n{content}",
            "content": f"请为标题为'{title}'的文章内容提供改进建议，使其更有吸引力:",
            "seo": f"请为标题为'{title}'的文章提供SEO优化建议，包括关键词建议:"
        }
        
        prompt = prompts.get(suggestion_type, prompts["content"])
        
        # 构建请求数据
        data = {
            "inputs": {},
            "query": prompt,
            "response_mode": "blocking",
            "user": "user123"  # 应该使用实际用户ID
        }
        
        # 发送请求
        # 注意: 实际上需要根据Dify的API文档调整endpoint和请求格式
        return self._make_request("completion", data=data)
    
    def generate_image(self, title, content, style="realistic"):
        """根据文章内容生成配图
        
        参数:
            title (str): 文章标题
            content (str): 文章内容
            style (str): 图片风格，可选值: 'realistic', 'cartoon', 'art'
        
        返回:
            dict: 包含生成图片URL的响应
        """
        # 提取文章摘要或关键段落作为图片生成提示
        content_summary = content[:200] if len(content) > 200 else content
        
        # 构建提示语
        prompt = f"根据标题'{title}'和内容摘要'{content_summary}'，生成一张{style}风格的配图"
        
        # 构建请求数据
        data = {
            "prompt": prompt,
            "style": style,
            "size": "1024x1024"
        }
        
        # 发送请求
        # 注意: 实际上需要根据Dify的图像生成API文档调整
        return self._make_request("images/generations", data=data)
    
    def publish_article(self, article_data):
        """发布文章到选定平台
        
        参数:
            article_data (dict): 包含文章信息的字典
                - title: 文章标题
                - content: 文章内容
                - platform: 发布平台
                - image: 配图URL
                
        返回:
            dict: 包含发布结果的响应
        """
        # 构建请求数据
        data = {
            "title": article_data.get("title", ""),
            "content": article_data.get("content", ""),
            "platform": article_data.get("platform", ""),
            "image_url": article_data.get("image", "")
        }
        
        # 发送请求
        # 注意: 实际接口需要根据Dify的文档调整
        return self._make_request("publish", data=data)