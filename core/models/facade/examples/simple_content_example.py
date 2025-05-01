"""简单内容管理器示例

展示如何使用SimpleContentManager管理临时内容对象。
"""

from core.models.facade.simple_content_manager import SimpleContentManager
from core.models.outline.basic_outline import OutlineNode
from core.models.research.basic_research import BasicResearch, KeyFinding, Source


def main():
    """主函数"""
    print("=== 简单内容管理器示例 ===")

    # 初始化
    SimpleContentManager.initialize()
    print("简单内容管理器已初始化")

    # 创建临时大纲
    print("\n--- 临时大纲示例 ---")
    outline = SimpleContentManager.create_basic_outline(
        title="临时大纲示例",
        description="这是一个通过SimpleContentManager创建的临时大纲",
        content_type="article",
        nodes=[
            OutlineNode(
                title="第一章：引言",
                level=1,
                content="介绍主题背景和研究意义"
            ),
            OutlineNode(
                title="第二章：文献综述",
                level=1,
                content="回顾相关研究成果"
            ),
            OutlineNode(
                title="第三章：研究方法",
                level=1,
                content="介绍研究方法和数据来源"
            )
        ]
    )
    print(f"已创建临时大纲: {outline.title}")

    # 保存临时大纲
    outline_id = SimpleContentManager.save_basic_outline(outline)
    print(f"临时大纲已保存，ID: {outline_id}")

    # 获取临时大纲
    retrieved_outline = SimpleContentManager.get_basic_outline(outline_id)
    if retrieved_outline:
        print(f"已获取临时大纲: {retrieved_outline.title}")
        print(f"大纲节点数量: {len(retrieved_outline.nodes)}")

        # 修改临时大纲
        retrieved_outline.description = "这是一个已更新的临时大纲"
        node4 = OutlineNode(
            title="第四章：研究结果",
            level=1,
            content="展示研究发现和数据分析"
        )
        retrieved_outline.nodes.append(node4)

        # 更新临时大纲
        SimpleContentManager.update_basic_outline(outline_id, retrieved_outline)
        print(f"临时大纲已更新，新节点数量: {len(retrieved_outline.nodes)}")

        # 再次获取
        updated_outline = SimpleContentManager.get_basic_outline(outline_id)
        if updated_outline:
            print(f"更新后的大纲描述: {updated_outline.description}")
            print(f"更新后的节点数量: {len(updated_outline.nodes)}")
        else:
            print("无法获取更新后的大纲")
    else:
        print("无法获取临时大纲")

    # 删除临时大纲
    SimpleContentManager.delete_basic_outline(outline_id)
    print(f"临时大纲已删除")

    # 创建临时研究
    print("\n--- 临时研究示例 ---")
    research = SimpleContentManager.create_basic_research(
        title="临时研究示例",
        background="这是一个通过SimpleContentManager创建的临时研究",
        content_type="article",
        key_findings=[
            KeyFinding(
                content="这是一个关键发现",
                importance=0.8,
                sources=[
                    Source(
                        name="示例来源",
                        url="https://example.com",
                        reliability_score=0.9
                    )
                ]
            )
        ]
    )
    print(f"已创建临时研究: {research.title}")

    # 保存临时研究
    research_id = SimpleContentManager.save_basic_research(research)
    print(f"临时研究已保存，ID: {research_id}")

    # 获取临时研究
    retrieved_research = SimpleContentManager.get_basic_research(research_id)
    if retrieved_research:
        print(f"已获取临时研究: {retrieved_research.title}")
        print(f"研究关键发现数量: {len(retrieved_research.key_findings)}")

        # 修改临时研究
        retrieved_research.background = "这是一个已更新的临时研究背景"
        new_finding = KeyFinding(
            content="这是另一个关键发现",
            importance=0.9
        )
        retrieved_research.key_findings.append(new_finding)

        # 更新临时研究
        SimpleContentManager.update_basic_research(research_id, retrieved_research)
        print(f"临时研究已更新，新关键发现数量: {len(retrieved_research.key_findings)}")

        # 再次获取
        updated_research = SimpleContentManager.get_basic_research(research_id)
        if updated_research:
            print(f"更新后的研究背景: {updated_research.background}")
            print(f"更新后的关键发现数量: {len(updated_research.key_findings)}")
        else:
            print("无法获取更新后的研究")
    else:
        print("无法获取临时研究")

    # 删除临时研究
    SimpleContentManager.delete_basic_research(research_id)
    print(f"临时研究已删除")

    print("=== 示例结束 ===")


if __name__ == "__main__":
    main()