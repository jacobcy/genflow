"""命令行入口"""
import argparse
from config import Config
from writer.article import ArticleGenerator

def main():
    """主函数"""
    # 创建参数解析器
    parser = argparse.ArgumentParser(description='AI 文章生成器')
    parser.add_argument('--topic', '-t', help='文章主题')
    parser.add_argument('--source', '-s', choices=['baidu', 'weibo', 'google'], help='热点来源')
    parser.add_argument('--style', default='新闻报道', choices=['新闻报道', '科技评测', '观点评论'], help='文章风格')
    parser.add_argument('--no-edit', action='store_true', help='不进行编辑改进')
    parser.add_argument('--no-save', action='store_true', help='不保存到文件')
    
    # 解析参数
    args = parser.parse_args()
    
    try:
        # 初始化生成器
        config = Config()
        generator = ArticleGenerator(config)
        
        # 生成文章
        if args.topic:
            # 从主题生成
            result = generator.generate_from_topic(
                topic=args.topic,
                style_name=args.style,
                do_edit=not args.no_edit,
                save_to_file=not args.no_save
            )
            
            # 输出结果
            if result['success']:
                print(f"\n主题: {args.topic}")
                print(f"风格: {args.style}")
                print("\n大纲:")
                print(result['outline'])
                print("\n原始文章:")
                print(result['original_article'])
                if result['edited_article']:
                    print("\n编辑后的文章:")
                    print(result['edited_article'])
                if result['original_file']:
                    print(f"\n原始文章已保存到: {result['original_file']}")
                if result['edited_file']:
                    print(f"编辑版文章已保存到: {result['edited_file']}")
            else:
                print(f"\n错误: {result['error']}")
                
        elif args.source or args.source == '':
            # 从热点生成
            results = generator.generate_from_trending(
                source=args.source,
                style_name=args.style,
                do_edit=not args.no_edit,
                save_to_file=not args.no_save
            )
            
            # 输出结果
            print(f"\n共生成 {len(results)} 篇文章:")
            for i, result in enumerate(results, 1):
                if result['success']:
                    print(f"\n{i}. 文章 {i}")
                    if result['original_file']:
                        print(f"原始文章: {result['original_file']}")
                    if result['edited_file']:
                        print(f"编辑版文章: {result['edited_file']}")
                else:
                    print(f"\n{i}. 文章 {i} 生成失败: {result['error']}")
                    
        else:
            parser.print_help()
            
    except KeyboardInterrupt:
        print("\n\n操作已取消")
    except Exception as e:
        print(f"\n发生错误: {str(e)}")

if __name__ == "__main__":
    main() 