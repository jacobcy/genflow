"""临时大纲存储示例

展示如何使用临时大纲存储功能。
"""

from core.models.outline import BasicOutline, OutlineNode, OutlineStorage, OutlineAdapter

def create_sample_outline() -> BasicOutline:
    """创建示例大纲"""
    # 创建节点
    node1 = OutlineNode(
        title="第一章：引言",
        level=1,
        content="介绍主题背景和研究意义"
    )
    
    node2 = OutlineNode(
        title="第二章：文献综述",
        level=1,
        content="回顾相关研究成果"
    )
    
    node3 = OutlineNode(
        title="第三章：研究方法",
        level=1,
        content="介绍研究方法和数据来源"
    )
    
    # 创建大纲
    outline = BasicOutline(
        title="研究论文大纲",
        description="这是一个研究论文的基本结构大纲",
        content_type="research_paper",
        nodes=[node1, node2, node3]
    )
    
    return outline

def main():
    """主函数"""
    print("=== 临时大纲存储示例 ===")
    
    # 初始化存储
    OutlineStorage.initialize()
    print("临时存储已初始化")
    
    # 创建示例大纲
    outline = create_sample_outline()
    print(f"已创建示例大纲: {outline.title}")
    
    # 保存到临时存储
    outline_id = OutlineStorage.save_outline(outline)
    print(f"大纲已保存到临时存储，ID: {outline_id}")
    
    # 从临时存储获取
    retrieved_outline = OutlineStorage.get_outline(outline_id)
    print(f"已从临时存储获取大纲: {retrieved_outline.title}")
    print(f"大纲节点数量: {len(retrieved_outline.nodes)}")
    
    # 修改大纲
    retrieved_outline.description = "这是一个已更新的研究论文大纲"
    node4 = OutlineNode(
        title="第四章：研究结果",
        level=1,
        content="展示研究发现和数据分析"
    )
    retrieved_outline.nodes.append(node4)
    
    # 更新临时存储
    OutlineStorage.update_outline(outline_id, retrieved_outline)
    print(f"大纲已更新，新节点数量: {len(retrieved_outline.nodes)}")
    
    # 再次获取
    updated_outline = OutlineStorage.get_outline(outline_id)
    print(f"更新后的大纲描述: {updated_outline.description}")
    print(f"更新后的节点数量: {len(updated_outline.nodes)}")
    
    # 列出所有大纲
    outline_ids = OutlineStorage.list_outlines()
    print(f"临时存储中的大纲数量: {len(outline_ids)}")
    
    # 删除大纲
    OutlineStorage.delete_outline(outline_id)
    print(f"大纲已从临时存储中删除")
    
    # 验证删除
    remaining_ids = OutlineStorage.list_outlines()
    print(f"删除后临时存储中的大纲数量: {len(remaining_ids)}")
    
    print("=== 示例结束 ===")

if __name__ == "__main__":
    main()