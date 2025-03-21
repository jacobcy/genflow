import requests
from bs4 import BeautifulSoup
import newspaper
from newspaper import Article
import ast
from openai import OpenAI
import os
from typing import List, Dict
import json
from datetime import datetime

class AIJournalist:
    def __init__(self, openai_api_key: str, serp_api_key: str):
        """初始化 AI 记者
        
        Args:
            openai_api_key: OpenAI API密钥
            serp_api_key: SERP API密钥
        """
        self.client = OpenAI(api_key=openai_api_key)
        self.serp_api_key = serp_api_key
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4-turbo-preview')
        
    def get_search_terms(self, topic: str) -> List[str]:
        """生成搜索关键词
        
        Args:
            topic: 文章主题
            
        Returns:
            搜索关键词列表
        """
        system_prompt = "你是一位资深记者。请为以下主题生成5个搜索关键词，用于研究和撰写文章。"
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"请为主题 '{topic}' 提供5个搜索关键词。请以Python列表格式返回，用逗号分隔。"}
            ],
            temperature=0.5
        )
        
        search_terms = ast.literal_eval(response.choices[0].message.content)
        return search_terms

    def get_search_results(self, search_term: str) -> List[Dict]:
        """执行搜索并获取结果
        
        Args:
            search_term: 搜索关键词
            
        Returns:
            搜索结果列表
        """
        url = f"https://serpapi.com/search.json?q={search_term}&api_key={self.serp_api_key}"
        response = requests.get(url)
        data = response.json()
        return data['organic_results']

    def select_relevant_urls(self, search_results: List[Dict]) -> List[str]:
        """从搜索结果中选择相关URL
        
        Args:
            search_results: 搜索结果列表
            
        Returns:
            相关URL列表
        """
        system_prompt = "你是一位记者助手。从给定的搜索结果中，选择最相关和最有信息价值的URL，用于撰写文章。"
        search_results_text = "\n".join([f"{i+1}. {result['link']}" for i, result in enumerate(search_results)])
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"搜索结果:\n{search_results_text}\n\n请选择最相关的URL编号。以Python列表格式返回，用逗号分隔。"}
            ],
            temperature=0.5
        )
        
        numbers = ast.literal_eval(response.choices[0].message.content)
        relevant_indices = [int(num) - 1 for num in numbers]
        relevant_urls = [search_results[i]['link'] for i in relevant_indices]
        return relevant_urls

    def get_article_text(self, url: str) -> str:
        """获取文章内容
        
        Args:
            url: 文章URL
            
        Returns:
            文章内容
        """
        article = Article(url)
        article.download()
        article.parse()
        return article.text

    def write_article(self, topic: str, article_texts: List[str]) -> str:
        """撰写文章
        
        Args:
            topic: 文章主题
            article_texts: 参考文章内容列表
            
        Returns:
            生成的文章
        """
        system_prompt = "你是一位资深记者。请基于提供的参考文章，撰写一篇高质量的新闻文章。文章应结构完整、信息丰富且引人入胜。"
        combined_text = "\n\n".join(article_texts)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"主题: {topic}\n\n参考文章:\n{combined_text}\n\n请撰写一篇高质量的新闻文章，要求:\n1. 结构完整\n2. 信息丰富\n3. 引人入胜\n4. 至少7个段落\n5. 注意引用和事实准确性"}
            ],
            temperature=0.7
        )
        
        return response.choices[0].message.content

    def edit_article(self, article: str) -> str:
        """编辑和改进文章
        
        Args:
            article: 原始文章
            
        Returns:
            编辑后的文章
        """
        # 获取编辑建议
        system_prompt = "你是一位资深编辑。请审查文章并提供改进建议，重点关注清晰度、连贯性和整体质量。"
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"文章:\n{article}\n\n请提供具体的改进建议。"}
            ],
            temperature=0.5
        )
        suggestions = response.choices[0].message.content

        # 根据建议重写文章
        system_prompt = "你是一位资深编辑。请根据改进建议重写文章。"
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"原文:\n{article}\n\n改进建议:\n{suggestions}\n\n请根据建议重写文章。"}
            ],
            temperature=0.7
        )
        
        return response.choices[0].message.content

    def save_article(self, topic: str, article: str, is_edited: bool = False):
        """保存文章到本地文件
        
        Args:
            topic: 文章主题
            article: 文章内容
            is_edited: 是否是编辑版本
        """
        # 创建 articles 目录（如果不存在）
        if not os.path.exists('articles'):
            os.makedirs('articles')
            
        # 生成文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"articles/{timestamp}_{topic.replace(' ', '_')}"
        filename += "_edited" if is_edited else ""
        filename += ".txt"
        
        # 保存文章
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(article)
        print(f"\n文章已保存到: {filename}")
        return filename

def generate_article(
    topic: str,
    do_edit: bool = False,
    openai_api_key: str = None,
    serp_api_key: str = None,
    save_to_file: bool = True
) -> dict:
    """生成文章的主要函数
    
    Args:
        topic: 文章主题
        do_edit: 是否需要编辑改进，默认False
        openai_api_key: OpenAI API密钥，如果为None则从环境变量获取
        serp_api_key: SERP API密钥，如果为None则从环境变量获取
        save_to_file: 是否保存到文件，默认True
        
    Returns:
        dict: 包含生成结果的字典，格式如下：
        {
            'success': bool,              # 是否成功
            'message': str,               # 状态信息
            'search_terms': List[str],    # 搜索关键词
            'relevant_urls': List[str],   # 相关链接
            'original_article': str,      # 原始文章
            'edited_article': str,        # 编辑后的文章（如果do_edit为True）
            'original_file': str,         # 原始文章保存路径（如果save_to_file为True）
            'edited_file': str,           # 编辑版文章保存路径（如果do_edit和save_to_file都为True）
            'error': str                  # 错误信息（如果有）
        }
    """
    result = {
        'success': False,
        'message': '',
        'search_terms': [],
        'relevant_urls': [],
        'original_article': '',
        'edited_article': '',
        'original_file': '',
        'edited_file': '',
        'error': ''
    }
    
    try:
        # 获取API密钥
        openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        serp_api_key = serp_api_key or os.getenv('SERP_API_KEY')
        
        if not openai_api_key or not serp_api_key:
            result['error'] = "未提供API密钥且环境变量中未设置 OPENAI_API_KEY 或 SERP_API_KEY"
            return result
            
        # 初始化AI记者
        journalist = AIJournalist(openai_api_key, serp_api_key)
        
        # 生成搜索关键词
        result['message'] = "正在生成搜索关键词..."
        search_terms = journalist.get_search_terms(topic)
        result['search_terms'] = search_terms
        
        # 搜索和筛选URL
        result['message'] = "正在搜索相关文章..."
        relevant_urls = []
        for term in search_terms:
            search_results = journalist.get_search_results(term)
            urls = journalist.select_relevant_urls(search_results)
            relevant_urls.extend(urls)
        result['relevant_urls'] = relevant_urls
        
        # 获取文章内容
        result['message'] = "正在获取文章内容..."
        article_texts = []
        for url in relevant_urls:
            try:
                text = journalist.get_article_text(url)
                if len(text) > 75:  # 忽略过短的文本
                    article_texts.append(text)
            except Exception as e:
                print(f"警告: 无法获取文章 {url}")
                
        # 写作文章
        result['message'] = "正在写作..."
        article = journalist.write_article(topic, article_texts)
        result['original_article'] = article
        
        if save_to_file:
            result['original_file'] = journalist.save_article(topic, article)
        
        # 编辑改进
        if do_edit:
            result['message'] = "正在编辑改进..."
            edited_article = journalist.edit_article(article)
            result['edited_article'] = edited_article
            if save_to_file:
                result['edited_file'] = journalist.save_article(topic, edited_article, is_edited=True)
        
        result['success'] = True
        result['message'] = "完成!"
        
    except Exception as e:
        result['success'] = False
        result['error'] = str(e)
        result['message'] = "生成过程中出现错误"
    
    return result

def main():
    """命令行入口函数"""
    try:
        # 获取用户输入
        topic = input("请输入要写作的主题: ")
        do_edit = input("是否需要自动编辑改进文章？(yes/no): ").lower().startswith('y')
        
        # 调用生成函数
        result = generate_article(topic, do_edit)
        
        # 输出结果
        if result['success']:
            print(f"\n搜索关键词: {', '.join(result['search_terms'])}")
            print(f"找到 {len(result['relevant_urls'])} 个相关链接")
            if result['original_file']:
                print(f"\n原始文章已保存到: {result['original_file']}")
            if result['edited_file']:
                print(f"编辑版文章已保存到: {result['edited_file']}")
            print("\n完成!")
        else:
            print(f"\n错误: {result['error']}")
            
    except KeyboardInterrupt:
        print("\n\n操作已取消")
    except Exception as e:
        print(f"\n发生错误: {str(e)}")

if __name__ == "__main__":
    main() 