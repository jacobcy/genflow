"""临时研究存储示例

展示如何使用临时研究存储功能。
"""

from core.models.research import BasicResearch, KeyFinding, Source, ExpertInsight, ResearchStorage, ResearchAdapter

def create_sample_research() -> BasicResearch:
    """创建示例研究"""
    # 创建关键发现
    key_findings = [
        KeyFinding(
            content="Python异步编程可以显著提高IO密集型应用的性能",
            importance=0.9,
            sources=[
                Source(
                    name="Python官方文档",
                    url="https://docs.python.org/3/library/asyncio.html",
                    reliability_score=1.0
                )
            ]
        ),
        KeyFinding(
            content="asyncio和threading不应混用，除非有特殊需求",
            importance=0.8,
            sources=[
                Source(
                    name="Python Asyncio最佳实践",
                    url="https://example.com/asyncio-best-practices",
                    reliability_score=0.85
                )
            ]
        )
    ]
    
    # 创建专家见解
    expert_insights = [
        ExpertInsight(
            expert_name="David Beazley",
            content="异步编程最大的挑战在于思维模式的转变，从顺序执行到事件驱动",
            field="Python开发",
            credentials="Python专家，著名讲师"
        ),
        ExpertInsight(
            expert_name="Łukasz Langa",
            content="Python 3.10中的结构化并发使asyncio更加安全和可靠",
            field="Python核心开发",
            credentials="Python核心开发者，PEP 8016的作者"
        )
    ]
    
    # 创建研究对象
    research = BasicResearch(
        title="Python异步编程最佳实践研究",
        content_type="tech_tutorial",
        background="异步编程是现代应用开发中的重要技术，特别是在处理IO密集型任务时",
        key_findings=key_findings,
        expert_insights=expert_insights,
        summary="本研究探讨了Python异步编程的最佳实践，包括何时使用asyncio，如何避免常见陷阱，以及与其他并发方案的比较"
    )
    
    return research

def main():
    """主函数"""
    print("=== 临时研究存储示例 ===")
    
    # 初始化存储
    ResearchStorage.initialize()
    print("临时存储已初始化")
    
    # 创建示例研究
    research = create_sample_research()
    print(f"已创建示例研究: {research.title}")
    
    # 保存到临时存储
    research_id = ResearchStorage.save_research(research)
    print(f"研究已保存到临时存储，ID: {research_id}")
    
    # 从临时存储获取
    retrieved_research = ResearchStorage.get_research(research_id)
    print(f"已从临时存储获取研究: {retrieved_research.title}")
    print(f"研究关键发现数量: {len(retrieved_research.key_findings)}")
    
    # 修改研究
    retrieved_research.summary = "这是一个已更新的研究摘要，包含了更多关于异步编程的见解"
    new_finding = KeyFinding(
        content="使用asyncio.gather可以并行执行多个协程",
        importance=0.7,
        sources=[
            Source(
                name="Real Python",
                url="https://realpython.com/async-io-python/",
                reliability_score=0.9
            )
        ]
    )
    retrieved_research.key_findings.append(new_finding)
    
    # 更新临时存储
    ResearchStorage.update_research(research_id, retrieved_research)
    print(f"研究已更新，新关键发现数量: {len(retrieved_research.key_findings)}")
    
    # 再次获取
    updated_research = ResearchStorage.get_research(research_id)
    print(f"更新后的研究摘要: {updated_research.summary}")
    print(f"更新后的关键发现数量: {len(updated_research.key_findings)}")
    
    # 列出所有研究
    research_ids = ResearchStorage.list_researches()
    print(f"临时存储中的研究数量: {len(research_ids)}")
    
    # 删除研究
    ResearchStorage.delete_research(research_id)
    print(f"研究已从临时存储中删除")
    
    # 验证删除
    remaining_ids = ResearchStorage.list_researches()
    print(f"删除后临时存储中的研究数量: {len(remaining_ids)}")
    
    print("=== 示例结束 ===")

if __name__ == "__main__":
    main()