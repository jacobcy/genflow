from ..dify_client import DifyClient
import logging
from flask import current_app
from datetime import datetime

logger = logging.getLogger(__name__)

class AIService:
    """提供AI功能的服务类"""
    
    def __init__(self):
        """初始化AI服务"""
        try:
            self.dify_client = DifyClient()
            self.is_available = True
        except Exception as e:
            logger.error(f"初始化AI服务失败: {str(e)}")
            self.is_available = False
    
    def get_title_suggestions(self, content):
        """获取标题建议
        
        参数:
            content (str): 文章内容
            
        返回:
            list: 标题建议列表
        """
        if not self.is_available:
            return {"error": "AI服务不可用"}
        
        try:
            # 调用Dify客户端获取标题建议
            response = self.dify_client.get_suggestion("", content, suggestion_type="title")
            
            # 解析响应获取建议列表
            if "error" in response:
                return {"error": response["error"]}
                
            # 简单处理，假设响应中有个answer字段包含建议
            # 实际处理方式取决于Dify API的响应格式
            suggestions = response.get("answer", "").split("\n")
            # 过滤掉空行和序号
            suggestions = [s.strip() for s in suggestions if s.strip()]
            suggestions = [s[2:].strip() if s[0].isdigit() and s[1] in ['.', '、', ':'] else s for s in suggestions]
            
            return {"suggestions": suggestions}
        except Exception as e:
            logger.error(f"获取标题建议失败: {str(e)}")
            return {"error": str(e)}
    
    def get_content_improvement(self, title, content):
        """获取内容改进建议
        
        参数:
            title (str): 文章标题
            content (str): 文章内容
            
        返回:
            dict: 内容改进建议
        """
        if not self.is_available:
            return {"error": "AI服务不可用"}
        
        try:
            # 调用Dify客户端获取内容改进建议
            response = self.dify_client.get_suggestion(title, content, suggestion_type="content")
            
            # 解析响应
            if "error" in response:
                return {"error": response["error"]}
                
            # 假设响应中有个answer字段包含建议
            improvement = response.get("answer", "")
            
            return {"improvement": improvement}
        except Exception as e:
            logger.error(f"获取内容改进建议失败: {str(e)}")
            return {"error": str(e)}
    
    def get_seo_suggestions(self, title, content):
        """获取SEO优化建议
        
        参数:
            title (str): 文章标题
            content (str): 文章内容
            
        返回:
            dict: SEO优化建议
        """
        if not self.is_available:
            return {"error": "AI服务不可用"}
        
        try:
            # 调用Dify客户端获取SEO建议
            response = self.dify_client.get_suggestion(title, content, suggestion_type="seo")
            
            # 解析响应
            if "error" in response:
                return {"error": response["error"]}
                
            # 假设响应中有个answer字段包含建议
            seo_suggestions = response.get("answer", "")
            
            return {"seo_suggestions": seo_suggestions}
        except Exception as e:
            logger.error(f"获取SEO建议失败: {str(e)}")
            return {"error": str(e)}
    
    def generate_article_image(self, title, content, style="realistic"):
        """生成文章配图
        
        参数:
            title (str): 文章标题
            content (str): 文章内容
            style (str): 图片风格
            
        返回:
            dict: 包含图片URL的结果
        """
        if not self.is_available:
            return {"error": "AI服务不可用"}
        
        try:
            # 调用Dify客户端生成图片
            response = self.dify_client.generate_image(title, content, style)
            
            # 解析响应
            if "error" in response:
                return {"error": response["error"]}
                
            # 假设响应中有个url字段包含图片URL
            image_url = response.get("data", [{}])[0].get("url", "")
            
            if not image_url:
                return {"error": "未能生成图片"}
                
            return {"image_url": image_url}
        except Exception as e:
            logger.error(f"生成文章配图失败: {str(e)}")
            return {"error": str(e)}
    
    def publish_to_platform(self, article_data):
        """发布文章到平台
        
        参数:
            article_data (dict): 文章数据
            
        返回:
            dict: 发布结果
        """
        if not self.is_available:
            return {"error": "AI服务不可用"}
        
        try:
            # 记录发布时间
            article_data["publish_time"] = datetime.now().isoformat()
            
            # 调用Dify客户端发布文章
            response = self.dify_client.publish_article(article_data)
            
            # 解析响应
            if "error" in response:
                return {"error": response["error"]}
                
            # 假设响应中有个url字段包含发布后的URL
            publish_url = response.get("url", "")
            
            return {
                "success": True,
                "publish_url": publish_url,
                "publish_time": article_data["publish_time"]
            }
        except Exception as e:
            logger.error(f"发布文章失败: {str(e)}")
            return {"error": str(e)} 