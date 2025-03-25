from typing import Dict, Optional
import openai
from ..core.config import settings

class AIService:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        
    async def process_message(self, message: str, context: Optional[str] = None) -> str:
        """Process a message using OpenAI's API"""
        try:
            messages = []
            if context:
                messages.append({"role": "system", "content": context})
            messages.append({"role": "user", "content": message})
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            # 实现降级机制
            return f"Error processing message: {str(e)}"
    
    async def analyze_content(self, content: str) -> Dict:
        """Analyze content using AI"""
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[{
                    "role": "system",
                    "content": "Analyze the following content and provide insights:"
                }, {
                    "role": "user",
                    "content": content
                }],
                temperature=0.3
            )
            return {
                "analysis": response.choices[0].message.content,
                "status": "success"
            }
        except Exception as e:
            return {
                "analysis": "Error analyzing content",
                "status": "error",
                "error": str(e)
            } 