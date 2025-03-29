"""控制器比较基准测试

该模块提供了一个统一的接口来比较不同的内容生产控制器实现，
允许对它们进行并行测试和性能评估。
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import json

from core.controllers.controller_adapter import (
    ContentControllerFactory,
    BaseContentControllerInterface
)
from core.models.platform.platform import Platform, get_default_platform
from core.models.topic.topic import Topic

# 配置日志
logger = logging.getLogger(__name__)

class ControllerBenchmark:
    """控制器比较基准测试

    提供统一接口对比不同控制器的性能和结果。
    """

    CONTROLLER_TYPES = {
        "custom_sequential": "自定义顺序流程 (ContentController)",
        "crewai_manager": "CrewAI层级流程 (CrewAIManagerController)",
        "crewai_sequential": "CrewAI标准顺序流程 (CrewAISequentialController)"
    }

    def __init__(self, model_name: str = "gpt-4"):
        """初始化控制器比较基准测试

        Args:
            model_name: 所有控制器使用的模型名称
        """
        self.model_name = model_name
        self.controllers = {}
        self.results = {}
        self.metrics = {}

    async def initialize_controllers(self, controller_types: Optional[List[str]] = None):
        """初始化指定类型的控制器

        Args:
            controller_types: 要初始化的控制器类型列表，如不提供则初始化所有类型
        """
        if controller_types is None:
            controller_types = list(self.CONTROLLER_TYPES.keys())

        # 获取默认平台
        platform = get_default_platform()

        for controller_type in controller_types:
            if controller_type not in self.CONTROLLER_TYPES:
                logger.warning(f"未知控制器类型: {controller_type}")
                continue

            logger.info(f"初始化控制器: {self.CONTROLLER_TYPES[controller_type]}")

            try:
                # 使用ContentControllerFactory创建控制器适配器
                controller = await ContentControllerFactory.create_controller(
                    controller_type=controller_type,
                    model_name=self.model_name,
                    platform=platform
                )
                self.controllers[controller_type] = controller

            except Exception as e:
                logger.error(f"初始化控制器'{controller_type}'失败: {str(e)}")

    async def run_benchmark(self,
                     category: str,
                     style: Optional[str] = None,
                     content_type: Optional[str] = None,
                     controller_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """运行基准测试，比较不同控制器的性能

        Args:
            category: 内容类别
            style: 写作风格
            content_type: 内容类型
            controller_types: 要测试的控制器类型，如不提供则测试所有已初始化的控制器

        Returns:
            Dict[str, Any]: 比较结果
        """
        if controller_types is None:
            controller_types = list(self.controllers.keys())

        # 确保所有请求的控制器都已初始化
        missing_controllers = [ct for ct in controller_types if ct not in self.controllers]
        if missing_controllers:
            await self.initialize_controllers(missing_controllers)

        # 记录开始时间
        start_time = datetime.now()
        logger.info(f"开始基准测试 - 类别: {category}, 风格: {style}, 内容类型: {content_type}")

        # 存储任务信息
        task_info = {
            "category": category,
            "style": style,
            "content_type": content_type,
            "start_time": start_time.isoformat(),
            "controllers": controller_types
        }

        # 逐个运行控制器
        for controller_type in controller_types:
            if controller_type not in self.controllers:
                logger.warning(f"控制器'{controller_type}'未初始化，跳过")
                continue

            controller = self.controllers[controller_type]
            logger.info(f"运行控制器: {self.CONTROLLER_TYPES[controller_type]}")

            # 记录控制器开始时间
            controller_start = time.time()

            try:
                # 使用统一的接口调用控制器
                result = await controller.produce_content(
                    category=category,
                    style=style,
                    content_type=content_type,
                    platform=None  # 不使用platform控制风格，而是通过style参数
                )

                # 记录执行时间和结果
                execution_time = time.time() - controller_start

                # 存储结果和指标
                self.results[controller_type] = result
                self.metrics[controller_type] = {
                    "execution_time": execution_time,
                    "success": result.get("status") == "success" or result.get("status") == "completed",
                    "completion_time": datetime.now().isoformat()
                }

                logger.info(f"控制器'{controller_type}'执行完成，耗时: {execution_time:.2f}秒")

            except Exception as e:
                logger.error(f"运行控制器'{controller_type}'失败: {str(e)}")
                self.metrics[controller_type] = {
                    "execution_time": time.time() - controller_start,
                    "success": False,
                    "error": str(e),
                    "completion_time": datetime.now().isoformat()
                }

        # 记录总执行时间
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()

        # 构建比较结果
        comparison = {
            "task_info": task_info,
            "total_execution_time": total_time,
            "end_time": end_time.isoformat(),
            "metrics": self.metrics,
            "results": self._sanitize_results(self.results)
        }

        return comparison

    def _sanitize_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """清理结果数据，移除不可序列化的内容

        Args:
            results: 原始结果数据

        Returns:
            Dict[str, Any]: 可序列化的结果数据
        """
        sanitized = {}

        for controller_type, result in results.items():
            if isinstance(result, dict):
                # 深度清理字典
                sanitized[controller_type] = self._deep_sanitize_dict(result)
            elif isinstance(result, list):
                # 清理列表中的每个元素
                sanitized_list = []
                for item in result:
                    if isinstance(item, dict):
                        sanitized_list.append(self._deep_sanitize_dict(item))
                    elif self._is_json_serializable(item):
                        sanitized_list.append(item)
                    else:
                        sanitized_list.append(str(item))
                sanitized[controller_type] = sanitized_list
            elif self._is_json_serializable(result):
                sanitized[controller_type] = result
            else:
                sanitized[controller_type] = str(result)

        return sanitized

    def _deep_sanitize_dict(self, data: Dict) -> Dict:
        """深度清理字典，确保所有内容都可序列化

        Args:
            data: 待清理的字典

        Returns:
            Dict: 清理后的字典
        """
        result = {}

        for key, value in data.items():
            if isinstance(value, dict):
                result[key] = self._deep_sanitize_dict(value)
            elif isinstance(value, list):
                sanitized_list = []
                for item in value:
                    if isinstance(item, dict):
                        sanitized_list.append(self._deep_sanitize_dict(item))
                    elif self._is_json_serializable(item):
                        sanitized_list.append(item)
                    else:
                        sanitized_list.append(str(item))
                result[key] = sanitized_list
            elif self._is_json_serializable(value):
                result[key] = value
            else:
                result[key] = str(value)

        return result

    def _is_json_serializable(self, obj: Any) -> bool:
        """检查对象是否可JSON序列化

        Args:
            obj: 待检查的对象

        Returns:
            bool: 是否可序列化
        """
        try:
            json.dumps(obj)
            return True
        except (TypeError, OverflowError):
            return False

    def generate_report(self, output_file: Optional[str] = None) -> str:
        """生成基准测试报告

        Args:
            output_file: 输出文件路径

        Returns:
            str: 报告内容
        """
        if not self.results or not self.metrics:
            return "没有可用的基准测试结果"

        # 构建报告内容
        report = []
        report.append("# 内容生产控制器基准测试报告")
        report.append(f"\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # 添加控制器列表
        report.append("\n## 测试控制器")
        for controller_type in self.metrics.keys():
            report.append(f"- {self.CONTROLLER_TYPES.get(controller_type, controller_type)}")

        # 添加性能对比
        report.append("\n## 性能对比")
        report.append("\n| 控制器 | 执行时间 | 成功状态 | 错误信息 |")
        report.append("| --- | --- | --- | --- |")

        for controller_type, metrics in self.metrics.items():
            controller_name = self.CONTROLLER_TYPES.get(controller_type, controller_type)
            execution_time = f"{metrics.get('execution_time', 0):.2f}秒"
            success = "✅ 成功" if metrics.get("success", False) else "❌ 失败"
            error = metrics.get("error", "-")

            report.append(f"| {controller_name} | {execution_time} | {success} | {error} |")

        # 添加内容质量对比
        report.append("\n## 内容质量对比")

        # 分别分析每个控制器的输出
        for controller_type, result in self.results.items():
            controller_name = self.CONTROLLER_TYPES.get(controller_type, controller_type)
            report.append(f"\n### {controller_name}")

            # 提取统一适配器格式的结果
            if "final_article" in result:
                article = result.get("final_article", {})
                title = article.get("title", "无标题")
                word_count = article.get("word_count", 0)

                report.append(f"\n标题: {title}")
                report.append(f"字数: {word_count}")
                report.append(f"状态: {result.get('status', '未知')}")

                # 添加内容摘要
                if "content" in article:
                    content = article.get("content", "")
                    summary = content[:200] + "..." if len(content) > 200 else content
                    report.append(f"\n内容摘要:\n```\n{summary}\n```")

            elif "final_articles" in result:
                articles = result.get("final_articles", [])
                report.append(f"\n生成文章数: {len(articles)}")

                for i, article in enumerate(articles[:3]):  # 只显示前3篇
                    title = article.get("title", f"文章{i+1}")
                    word_count = article.get("word_count", 0)

                    report.append(f"\n#### 文章{i+1}: {title}")
                    report.append(f"字数: {word_count}")

                    # 添加内容摘要
                    if "content" in article:
                        content = article.get("content", "")
                        summary = content[:100] + "..." if len(content) > 100 else content
                        report.append(f"\n摘要:\n```\n{summary}\n```")

            elif "final_output" in result:
                output = result.get("final_output", "")
                if isinstance(output, dict) and "title" in output:
                    title = output.get("title", "无标题")
                    report.append(f"\n标题: {title}")

                # 提取内容
                content = ""
                if isinstance(output, str):
                    content = output
                elif isinstance(output, dict) and "content" in output:
                    content = output.get("content", "")

                summary = content[:200] + "..." if len(content) > 200 else content
                report.append(f"\n内容摘要:\n```\n{summary}\n```")
                report.append(f"\n执行时间: {result.get('execution_time', 0)}秒")

            # 检查是否有content_type
            if "content_type" in result:
                report.append(f"内容类型: {result['content_type']}")

        # 保存报告
        report_content = "\n".join(report)

        if output_file:
            try:
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(report_content)
                logger.info(f"报告已保存到: {output_file}")
            except Exception as e:
                logger.error(f"保存报告失败: {str(e)}")

        return report_content


# 使用示例
async def main():
    """主函数"""
    try:
        # 创建基准测试实例
        benchmark = ControllerBenchmark()

        # 初始化所有控制器
        await benchmark.initialize_controllers()

        # 运行基准测试
        result = await benchmark.run_benchmark(
            category="科技",
            style="专业",
            content_type="分析"  # 添加内容类型参数
        )

        # 生成报告
        report = benchmark.generate_report("benchmark_report.md")

        # 打印摘要
        print("\n=== 基准测试完成 ===")
        print(f"测试控制器: {', '.join(result['metrics'].keys())}")
        print(f"总执行时间: {result['total_execution_time']:.2f}秒")

        for controller, metrics in result["metrics"].items():
            print(f"\n{benchmark.CONTROLLER_TYPES.get(controller, controller)}:")
            print(f"  执行时间: {metrics.get('execution_time', 0):.2f}秒")
            print(f"  状态: {'成功' if metrics.get('success', False) else '失败'}")
            if "error" in metrics:
                print(f"  错误: {metrics['error']}")

    except Exception as e:
        print(f"基准测试失败: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
