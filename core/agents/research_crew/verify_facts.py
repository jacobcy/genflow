from core.agents.research_crew.research_protocol import FactVerificationRequest, FactVerificationResponse
from core.agents.research_crew.research_result import ResearchWorkflowResult
from core.models.feedback import ResearchFeedback
from core.models.research.research import BasicResearch

import logging

logger = logging.getLogger("research_crew")

from crewai import Task, Crew

async def verify_facts(
        self,
        request: FactVerificationRequest
    ) -> FactVerificationResponse:
        """验证事实陈述的准确性

        根据提供的陈述列表，执行事实验证流程，返回验证结果。

        Args:
            request: 事实验证请求对象，包含陈述、验证彻底程度和选项

        Returns:
            FactVerificationResponse: 验证结果响应对象
        """
        logger.info(f"开始验证 {len(request.statements)} 个事实陈述")
        try:
            # 根据thoroughness设置验证深度
            if request.thoroughness == "low":
                search_depth = 1
                confidence_threshold = 0.6
            elif request.thoroughness == "high":
                search_depth = 3
                confidence_threshold = 0.8
            else:
                # medium
                search_depth = 2
                confidence_threshold = 0.7

            # 准备验证结果
            verification_results = []

            # 对每个陈述进行验证
            for statement in request.statements:
                logger.info(f"验证陈述: {statement}")

                # 创建验证任务
                verify_task = Task(
                    description=f"对陈述进行事实验证: '{statement}'。提供详细的分析和至少{search_depth}个来源。" +
                              f"评估置信度，必须超过{confidence_threshold}才能判定为真。",
                    expected_output="验证结果，包含陈述评估、验证状态(真/假/不确定)、置信度和来源",
                    agent=self.agents.get("fact_checker", self.agents["background_researcher"])
                )

                # 执行验证任务
                verify_crew = Crew(
                    agents=[self.agents.get("fact_checker", self.agents["background_researcher"])],
                    tasks=[verify_task],
                    verbose=True
                )
                verify_result = verify_crew.kickoff()

                # 解析验证结果
                result_text = str(verify_result[0])

                # 简单的结果解析逻辑（实际应用中可能需要更复杂的提取和解析）
                verified = None
                confidence = 0.0
                explanation = ""
                sources = []

                # 从结果文本中提取关键信息
                if "真实" in result_text or "正确" in result_text or "True" in result_text:
                    verified = True
                elif "虚假" in result_text or "错误" in result_text or "False" in result_text:
                    verified = False
                else:
                    verified = None  # 不确定

                # 提取置信度（简化逻辑）
                confidence_markers = [
                    "置信度", "信心", "confidence", "可信度", "确信度"
                ]
                for marker in confidence_markers:
                    if marker in result_text:
                        idx = result_text.find(marker)
                        # 寻找数字
                        for i in range(idx, min(idx + 50, len(result_text))):
                            if result_text[i].isdigit() or result_text[i] == '.':
                                # 尝试提取数字
                                num_start = i
                                while i < len(result_text) and (result_text[i].isdigit() or result_text[i] == '.'):
                                    i += 1
                                num_end = i
                                try:
                                    confidence_value = float(result_text[num_start:num_end])
                                    # 归一化置信度到0-1范围
                                    if confidence_value > 1:
                                        confidence_value /= 10
                                    if 0 <= confidence_value <= 1:
                                        confidence = confidence_value
                                        break
                                except ValueError:
                                    pass

                # 提取解释
                explanation_markers = [
                    "解释", "分析", "说明", "explanation", "analysis"
                ]
                for marker in explanation_markers:
                    if marker in result_text:
                        idx = result_text.find(marker)
                        marker_end = idx + len(marker) + 1
                        # 寻找解释的结束位置（下一个标题或空行）
                        explanation_end = result_text.find("\n\n", marker_end)
                        if explanation_end == -1:
                            explanation_end = len(result_text)
                        explanation = result_text[marker_end:explanation_end].strip()
                        if explanation:
                            break

                if not explanation:
                    # 如果没有找到明确的解释，使用整个文本
                    explanation = result_text

                # 提取来源
                source_markers = [
                    "来源", "参考", "source", "reference"
                ]
                for marker in source_markers:
                    if marker in result_text:
                        idx = result_text.find(marker)
                        # 从标记位置开始到结尾的文本
                        remaining_text = result_text[idx:]
                        # 按行分割
                        lines = remaining_text.split("\n")
                        for line in lines[1:]:  # 跳过标记行
                            line = line.strip()
                            if line and line[0] in ['-', '*', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                                # 提取来源名称和URL
                                source_line = line.lstrip('-*0123456789. ')
                                url = None
                                if "http" in source_line:
                                    url_start = source_line.find("http")
                                    url_end = source_line.find(" ", url_start) if source_line.find(" ", url_start) > 0 else len(source_line)
                                    url = source_line[url_start:url_end].strip(",.()\"'")
                                    source_name = source_line[:url_start].strip() or "参考资料"
                                else:
                                    source_name = source_line

                                sources.append({
                                    "name": source_name,
                                    "url": url
                                })
                            elif line.startswith("#") or line.startswith("结论") or line.startswith("Conclusion"):
                                # 遇到新的标题或结论部分，结束来源提取
                                break

                # 汇总验证结果
                verification_result = {
                    "statement": statement,
                    "verified": verified,
                    "confidence": confidence or 0.5,  # 默认置信度为0.5
                    "explanation": explanation or "未提供详细解释",
                    "sources": sources
                }
                verification_results.append(verification_result)

            # 创建响应对象
            response = FactVerificationResponse(
                results=verification_results,
                metadata={
                    "thoroughness": request.thoroughness,
                    "verification_time": datetime.now().isoformat(),
                    "options": request.options
                }
            )

            logger.info(f"事实验证完成，验证了 {len(verification_results)} 个陈述")
            return response

        except Exception as e:
            logger.error(f"事实验证过程中出错: {e}")
            raise RuntimeError(f"事实验证失败: {str(e)}")
