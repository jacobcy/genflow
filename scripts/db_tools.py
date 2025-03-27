#!/usr/bin/env python3
"""
GenFlow 数据库管理工具

该工具提供了数据库管理相关的功能，包括：
1. 数据库初始化和全量同步
2. 配置检查和查询
3. 数据库状态查看

用法:
  python db_tools.py [命令]

命令:
  init       - 初始化数据库并执行完整同步（删除不存在的配置）
  status     - 查看数据库状态和配置数量
  check      - 检查配置文件和数据库的一致性
  content    - 列出所有内容类型
  styles     - 列出所有文章风格
  platforms  - 列出所有平台配置
  help       - 显示帮助信息
"""

import os
import sys
import sqlite3
from loguru import logger

def init_db():
    """初始化数据库并执行完整同步"""
    print("正在初始化数据库并执行完整同步...")

    try:
        from scripts.initialize_database import main
        success = main()
        if success:
            print("✓ 数据库初始化和完整同步成功完成！")
        else:
            print("✗ 数据库初始化或同步过程中发生错误，详情请查看日志")
    except Exception as e:
        print(f"✗ 错误: {str(e)}")

def check_db_status():
    """检查数据库状态和配置数量"""
    print("检查数据库状态...")

    try:
        # 检查数据库文件是否存在
        db_path = os.path.join("core", "data", "genflow.db")
        if not os.path.exists(db_path):
            print(f"✗ 数据库文件不存在: {db_path}")
            print("提示: 请先运行 `python db_tools.py init` 来初始化数据库")
            return

        # 连接数据库并获取表信息
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 查询表结构
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()

        print(f"✓ 数据库文件存在: {db_path}")
        print(f"✓ 数据库包含 {len(tables)} 个表:")

        # 获取各表中的记录数
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  - {table_name}: {count} 条记录")

        conn.close()
    except Exception as e:
        print(f"✗ 错误: {str(e)}")

def check_consistency():
    """检查配置文件和数据库的一致性"""
    print("检查配置文件和数据库的一致性...")

    try:
        # 初始化ContentManager，使用数据库模式
        from core.models.content_manager import ContentManager
        ContentManager.initialize(use_db=True)

        # 获取数据库和文件中的配置
        db_content_types = ContentManager.get_all_content_types()

        # 临时切换到文件模式，获取文件中的配置
        ContentManager._is_initialized = False
        ContentManager.initialize(use_db=False)
        file_content_types = ContentManager.get_all_content_types()

        # 比较内容类型
        db_ids = set(db_content_types.keys())
        file_ids = set(file_content_types.keys())

        print("\n内容类型对比:")
        print(f"  - 数据库中: {len(db_ids)} 个内容类型")
        print(f"  - 文件中: {len(file_ids)} 个内容类型")

        if db_ids == file_ids:
            print("  ✓ 内容类型ID完全一致")
        else:
            print("  ✗ 内容类型ID不一致:")
            if db_ids - file_ids:
                print(f"    - 仅在数据库中存在: {', '.join(db_ids - file_ids)}")
            if file_ids - db_ids:
                print(f"    - 仅在文件中存在: {', '.join(file_ids - db_ids)}")

        # 同样检查其他配置...
        # 文章风格
        db_styles = ContentManager.get_all_article_styles()
        ContentManager._is_initialized = False
        ContentManager.initialize(use_db=False)
        file_styles = ContentManager.get_all_article_styles()

        db_style_ids = set(db_styles.keys())
        file_style_ids = set(file_styles.keys())

        print("\n文章风格对比:")
        print(f"  - 数据库中: {len(db_style_ids)} 个文章风格")
        print(f"  - 文件中: {len(file_style_ids)} 个文章风格")

        if db_style_ids == file_style_ids:
            print("  ✓ 文章风格ID完全一致")
        else:
            print("  ✗ 文章风格ID不一致:")
            if db_style_ids - file_style_ids:
                print(f"    - 仅在数据库中存在: {', '.join(db_style_ids - file_style_ids)}")
            if file_style_ids - db_style_ids:
                print(f"    - 仅在文件中存在: {', '.join(file_style_ids - db_style_ids)}")

        # 平台配置
        db_platforms = ContentManager.get_all_platforms()
        ContentManager._is_initialized = False
        ContentManager.initialize(use_db=False)
        file_platforms = ContentManager.get_all_platforms()

        db_platform_ids = set(db_platforms.keys())
        file_platform_ids = set(file_platforms.keys())

        print("\n平台配置对比:")
        print(f"  - 数据库中: {len(db_platform_ids)} 个平台配置")
        print(f"  - 文件中: {len(file_platform_ids)} 个平台配置")

        if db_platform_ids == file_platform_ids:
            print("  ✓ 平台配置ID完全一致")
        else:
            print("  ✗ 平台配置ID不一致:")
            if db_platform_ids - file_platform_ids:
                print(f"    - 仅在数据库中存在: {', '.join(db_platform_ids - file_platform_ids)}")
            if file_platform_ids - db_platform_ids:
                print(f"    - 仅在文件中存在: {', '.join(file_platform_ids - db_platform_ids)}")
    except Exception as e:
        print(f"✗ 错误: {str(e)}")

def list_content_types():
    """列出所有内容类型"""
    print("列出所有内容类型...")

    try:
        # 初始化ContentManager，使用数据库模式
        from core.models.content_manager import ContentManager
        ContentManager.initialize(use_db=True)

        # 获取所有内容类型
        content_types = ContentManager.get_all_content_types()

        print(f"共有 {len(content_types)} 个内容类型:")
        for id, ct in content_types.items():
            print(f"  - {id}: {ct.name}")
            print(f"    描述: {getattr(ct, 'description', '无')}")
            print(f"    默认字数: {getattr(ct, 'default_word_count', '无')}")
            print(f"    启用状态: {'已启用' if getattr(ct, 'is_enabled', True) else '已禁用'}")
            print()
    except Exception as e:
        print(f"✗ 错误: {str(e)}")

def list_article_styles():
    """列出所有文章风格"""
    print("列出所有文章风格...")

    try:
        # 初始化ContentManager，使用数据库模式
        from core.models.content_manager import ContentManager
        ContentManager.initialize(use_db=True)

        # 获取所有文章风格
        styles = ContentManager.get_all_article_styles()

        print(f"共有 {len(styles)} 个文章风格:")
        for id, style in styles.items():
            print(f"  - {id}: {style.name}")
            print(f"    描述: {getattr(style, 'description', '无')}")
            print(f"    语调: {getattr(style, 'tone', '无')}")
            print(f"    启用状态: {'已启用' if getattr(style, 'is_enabled', True) else '已禁用'}")
            print()
    except Exception as e:
        print(f"✗ 错误: {str(e)}")

def list_platforms():
    """列出所有平台配置"""
    print("列出所有平台配置...")

    try:
        # 初始化ContentManager，使用数据库模式
        from core.models.content_manager import ContentManager
        ContentManager.initialize(use_db=True)

        # 获取所有平台配置
        platforms = ContentManager.get_all_platforms()

        print(f"共有 {len(platforms)} 个平台配置:")
        for id, platform in platforms.items():
            print(f"  - {id}: {platform.name}")
            print(f"    描述: {getattr(platform, 'description', '无')}")
            print(f"    平台类型: {getattr(platform, 'platform_type', '无')}")
            print(f"    URL: {getattr(platform, 'url', '无')}")
            print(f"    启用状态: {'已启用' if getattr(platform, 'is_enabled', True) else '已禁用'}")
            print()
    except Exception as e:
        print(f"✗ 错误: {str(e)}")

def show_help():
    """显示帮助信息"""
    print(__doc__)

def main():
    """主函数"""
    # 解析命令行参数
    if len(sys.argv) < 2:
        show_help()
        return

    command = sys.argv[1].lower()

    # 根据命令执行相应的功能
    if command == "init":
        init_db()
    elif command == "status":
        check_db_status()
    elif command == "check":
        check_consistency()
    elif command == "content":
        list_content_types()
    elif command == "styles":
        list_article_styles()
    elif command == "platforms":
        list_platforms()
    elif command == "help":
        show_help()
    else:
        print(f"未知命令: {command}")
        show_help()

if __name__ == "__main__":
    main()
