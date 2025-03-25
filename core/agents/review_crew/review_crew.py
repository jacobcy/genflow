"""审核团队工作流程"""
from typing import List, Dict, Optional
from datetime import datetime
from crewai import Task, Crew, Process
from core.models.article import Article
from core.models.platform import Platform
from .review_agents import ReviewAgents

class ReviewResult:
    """审核结果"""
    def __init__(
        self,
        article: Article,
        plagiarism_report: Dict,
        ai_detection_report: Dict,
        content_review_report: Dict,
        final_review: Dict
    ):
        self.article = article
        self.plagiarism_report = plagiarism_report
        self.ai_detection_report = ai_detection_report
        self.content_review_report = content_review_report
        self.final_review = final_review
        self.created_at = datetime.now()
        self.human_feedback: Optional[Dict] = None

class ReviewCrew:
    """审核团队"""
    
    def __init__(self):
        """初始化团队"""
        self.agents = ReviewAgents()
        self.plagiarism_checker = self.agents.create_plagiarism_checker()
        self.ai_detector = self.agents.create_ai_detector()
        self.content_reviewer = self.agents.create_content_reviewer()
        self.final_reviewer = self.agents.create_final_reviewer()
    
    async def review_article(self, article: Article, platform: Platform) -> ReviewResult:
        """审核文章
        
        Args:
            article: 要审核的文章
            platform: 目标平台
            
        Returns:
            ReviewResult: 审核结果
        """
        # 1. 查重任务
        plagiarism_task = Task(
            description=f"""
            1. 检查文章"{article.title}"的原创性
            2. 分析重复内容
            3. 检查引用规范
            4. 评估原创度
            5. 提供修改建议
            """,
            agent=self.plagiarism_checker
        )
        
        # 2. AI检测任务
        ai_detection_task = Task(
            description=f"""
            1. 分析文章的语言特征
            2. 识别机器生成内容
            3. 评估人工痕迹
            4. 检查平台规范
            5. 提供优化建议
            """,
            agent=self.ai_detector
        )
        
        # 3. 内容审核任务
        content_review_task = Task(
            description=f"""
            1. 检查内容合规性
            2. 识别敏感信息
            3. 审核表述方式
            4. 评估价值导向
            5. 提供整改建议
            """,
            agent=self.content_reviewer
        )
        
        # 4. 终审任务
        final_review_task = Task(
            description=f"""
            1. 整合各项审核结果
            2. 评估整体质量
            3. 判断发布风险
            4. 给出修改方向
            5. 制定最终结论
            """,
            agent=self.final_reviewer
        )
        
        # 创建工作流
        crew = Crew(
            agents=[
                self.plagiarism_checker,
                self.ai_detector,
                self.content_reviewer,
                self.final_reviewer
            ],
            tasks=[
                plagiarism_task,
                ai_detection_task,
                content_review_task,
                final_review_task
            ],
            process=Process.sequential
        )
        
        # 执行工作流
        result = crew.kickoff()
        
        # 整理审核结果
        review_result = ReviewResult(
            article=article,
            plagiarism_report=result["plagiarism_report"],
            ai_detection_report=result["ai_detection_report"],
            content_review_report=result["content_review_report"],
            final_review=result["final_review"]
        )
        
        return review_result
    
    def get_human_feedback(self, review_result: ReviewResult) -> ReviewResult:
        """获取人工反馈
        
        Args:
            review_result: 审核结果
            
        Returns:
            ReviewResult: 更新后的审核结果
        """
        print("\n=== 审核报告评估 ===\n")
        print(f"文章: {review_result.article.title}")
        
        print("\n1. 查重报告质量 (0-1):")
        print("- 分析深度")
        print("- 问题定位")
        print("- 建议可行性")
        plagiarism_score = float(input("请评分: "))
        
        print("\n2. AI检测报告质量 (0-1):")
        print("- 特征分析")
        print("- 结论准确性")
        print("- 优化建议")
        ai_score = float(input("请评分: "))
        
        print("\n3. 内容审核报告质量 (0-1):")
        print("- 风险识别")
        print("- 合规评估")
        print("- 整改方案")
        content_score = float(input("请评分: "))
        
        print("\n4. 修改意见:")
        comments = input("评估意见: ")
        
        # 更新反馈
        review_result.human_feedback = {
            "plagiarism_score": plagiarism_score,
            "ai_score": ai_score,
            "content_score": content_score,
            "average_score": (plagiarism_score + ai_score + content_score) / 3,
            "comments": comments,
            "reviewed_at": datetime.now()
        }
        
        return review_result
    
    def update_article_status(self, review_result: ReviewResult) -> Article:
        """更新文章状态
        
        Args:
            review_result: 审核结果
            
        Returns:
            Article: 更新后的文章
        """
        # 获取最终审核结果
        final_review = review_result.final_review
        
        # 更新文章
        article = review_result.article
        article.review_data = {
            "plagiarism_rate": final_review["plagiarism_rate"],
            "ai_score": final_review["ai_score"],
            "risk_level": final_review["risk_level"],
            "review_comments": final_review["comments"],
            "reviewed_at": datetime.now()
        }
        
        # 更新状态
        if final_review["risk_level"] == "low":
            article.status = "approved"
        elif final_review["risk_level"] == "medium":
            article.status = "needs_revision"
        else:
            article.status = "rejected"
        
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
            {
                "title": "异步编程简介",
                "content": "..."
            }
        ],
        status="pending_review"
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
    
    # 创建审核团队
    crew = ReviewCrew()
    
    # 进行审核
    review_result = await crew.review_article(article, platform)
    
    # 获取人工反馈
    review_result = crew.get_human_feedback(review_result)
    
    # 如果评分达标，更新文章状态
    if review_result.human_feedback["average_score"] >= 0.7:
        article = crew.update_article_status(review_result)
        print("\n=== 审核结果 ===")
        print(f"文章: {article.title}")
        print(f"状态: {article.status}")
        print(f"查重率: {article.review_data['plagiarism_rate']}")
        print(f"AI分数: {article.review_data['ai_score']}")
        print(f"风险等级: {article.review_data['risk_level']}")
        print(f"审核意见: {article.review_data['review_comments']}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 