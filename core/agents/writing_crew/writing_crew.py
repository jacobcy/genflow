"""写作团队工作流程"""
from typing import List, Dict, Optional
from datetime import datetime
from crewai import Task, Crew, Process
from core.models.article import Article, Section
from core.models.platform import Platform
from .writing_agents import WritingAgents

class WritingResult:
    """写作结果"""
    def __init__(
        self,
        article: Article,
        outline: Dict,
        content: Dict,
        seo_data: Dict,
        final_draft: Dict
    ):
        self.article = article
        self.outline = outline
        self.content = content
        self.seo_data = seo_data
        self.final_draft = final_draft
        self.created_at = datetime.now()
        self.human_feedback: Optional[Dict] = None

class WritingCrew:
    """写作团队"""
    
    def __init__(self):
        """初始化团队"""
        self.agents = WritingAgents()
        self.outline_writer = self.agents.create_outline_writer()
        self.content_writer = self.agents.create_content_writer()
        self.seo_optimizer = self.agents.create_seo_optimizer()
        self.editor = self.agents.create_editor()
    
    async def write_article(self, article: Article, platform: Platform) -> WritingResult:
        """写作文章
        
        Args:
            article: 文章信息
            platform: 目标平台
            
        Returns:
            WritingResult: 写作结果
        """
        # 1. 大纲优化任务
        outline_task = Task(
            description=f"""
            1. 分析文章"{article.title}"的大纲
            2. 根据平台"{platform.name}"的要求优化结构
            3. 设计引人入胜的开头
            4. 规划重点论述部分
            5. 设计有力的结尾
            """,
            agent=self.outline_writer
        )
        
        # 2. 内容写作任务
        content_task = Task(
            description=f"""
            1. 根据优化后的大纲撰写内容
            2. 确保专业性和准确性
            3. 使用生动的案例
            4. 加入适当的过渡
            5. 注意文章的节奏感
            """,
            agent=self.content_writer
        )
        
        # 3. SEO优化任务
        seo_task = Task(
            description=f"""
            1. 分析目标平台的SEO要求
            2. 优化标题和关键词
            3. 调整内容结构
            4. 优化元描述
            5. 提供SEO建议
            """,
            agent=self.seo_optimizer
        )
        
        # 4. 编辑优化任务
        edit_task = Task(
            description=f"""
            1. 全面审查文章内容
            2. 优化表达方式
            3. 确保逻辑连贯
            4. 提升可读性
            5. 完善细节
            """,
            agent=self.editor
        )
        
        # 创建工作流
        crew = Crew(
            agents=[
                self.outline_writer,
                self.content_writer,
                self.seo_optimizer,
                self.editor
            ],
            tasks=[
                outline_task,
                content_task,
                seo_task,
                edit_task
            ],
            process=Process.sequential
        )
        
        # 执行工作流
        result = crew.kickoff()
        
        # 整理写作结果
        writing_result = WritingResult(
            article=article,
            outline=result["outline"],
            content=result["content"],
            seo_data=result["seo_data"],
            final_draft=result["final_draft"]
        )
        
        return writing_result
    
    def get_human_feedback(self, writing_result: WritingResult) -> WritingResult:
        """获取人工反馈
        
        Args:
            writing_result: 写作结果
            
        Returns:
            WritingResult: 更新后的写作结果
        """
        print("\n=== 文章评审 ===\n")
        print(f"标题: {writing_result.article.title}")
        
        print("\n1. 内容质量 (0-1):")
        print("- 专业性")
        print("- 可读性")
        print("- 完整性")
        content_score = float(input("请评分: "))
        
        print("\n2. 结构设计 (0-1):")
        print("- 逻辑性")
        print("- 层次感")
        print("- 过渡自然")
        structure_score = float(input("请评分: "))
        
        print("\n3. SEO表现 (0-1):")
        print("- 关键词优化")
        print("- 标题吸引力")
        print("- 元描述质量")
        seo_score = float(input("请评分: "))
        
        print("\n4. 修改建议:")
        comments = input("评审意见: ")
        
        # 更新反馈
        writing_result.human_feedback = {
            "content_score": content_score,
            "structure_score": structure_score,
            "seo_score": seo_score,
            "average_score": (content_score + structure_score + seo_score) / 3,
            "comments": comments,
            "reviewed_at": datetime.now()
        }
        
        return writing_result
    
    def update_article(self, writing_result: WritingResult) -> Article:
        """更新文章
        
        Args:
            writing_result: 写作结果
            
        Returns:
            Article: 更新后的文章
        """
        # 从最终稿中提取信息
        final_draft = writing_result.final_draft
        
        # 更新文章
        article = writing_result.article
        article.title = final_draft["title"]
        article.summary = final_draft["summary"]
        article.sections = [
            Section(
                title=section["title"],
                content=section["content"],
                order=idx + 1
            )
            for idx, section in enumerate(final_draft["sections"])
        ]
        article.seo_data = writing_result.seo_data
        article.status = "reviewed"
        
        return article

# 使用示例
async def main():
    # 创建一个示例文章
    article = Article(
        id="article_001",
        topic_id="topic_001",
        title="Python异步编程最佳实践",
        summary="探讨Python异步编程的发展、应用场景和最佳实践",
        sections=[
            Section(
                title="异步编程简介",
                content="...",
                order=1
            )
        ],
        status="draft"
    )
    
    # 创建一个示例平台
    platform = Platform(
        id="platform_001",
        name="掘金",
        url="https://juejin.cn",
        content_rules={
            "min_words": 1000,
            "max_words": 5000,
            "allowed_tags": ["Python", "编程", "技术"]
        }
    )
    
    # 创建写作团队
    crew = WritingCrew()
    
    # 进行写作
    writing_result = await crew.write_article(article, platform)
    
    # 获取人工反馈
    writing_result = crew.get_human_feedback(writing_result)
    
    # 如果评分达标，更新文章
    if writing_result.human_feedback["average_score"] >= 0.7:
        article = crew.update_article(writing_result)
        print("\n=== 更新后的文章 ===")
        print(f"标题: {article.title}")
        print(f"摘要: {article.summary}")
        print("\n章节:")
        for section in article.sections:
            print(f"\n{section.order}. {section.title}")
            print(section.content)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 