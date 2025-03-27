"""
测试ArticleProductionProgress模块

专注测试ArticleProductionProgress的核心功能，包括进度管理、阶段转换和状态更新。
focus on testing the core functions of the ArticleProductionProgress.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

# 导入被测试模块
from core.models.progress import ArticleProductionProgress
from core.models.enums import ProductionStage, StageStatus

class TestArticleProductionProgressInitialization:
    """测试ArticleProductionProgress的初始化功能"""

    def test_init_with_article(self):
        """测试使用文章对象初始化"""
        # 准备模拟数据
        mock_article = MagicMock()
        mock_article.id = "article123"

        # 初始化进度对象
        progress = ArticleProductionProgress(article=mock_article)

        # 验证结果
        assert progress.article == mock_article
        assert progress.article_id == "article123"
        assert progress.current_stage == ProductionStage.TOPIC_DISCOVERY
        assert progress.completed_at is None
        assert len(progress.stages) == len(ProductionStage)
        assert progress.stages[ProductionStage.TOPIC_DISCOVERY]["status"] == StageStatus.PENDING

    def test_init_with_article_id(self):
        """测试使用文章ID初始化"""
        # 初始化进度对象
        progress = ArticleProductionProgress(article_id="article456")

        # 验证结果
        assert progress.article is None
        assert progress.article_id == "article456"
        assert progress.current_stage == ProductionStage.TOPIC_DISCOVERY

    def test_init_without_article_or_id(self):
        """测试不提供文章或ID初始化"""
        # 初始化进度对象
        progress = ArticleProductionProgress()

        # 验证结果
        assert progress.article is None
        assert progress.article_id is None
        assert progress.current_stage == ProductionStage.TOPIC_DISCOVERY

class TestArticleProductionProgressStageManagement:
    """测试ArticleProductionProgress的阶段管理功能"""

    def setup_method(self):
        """每个测试方法前的设置"""
        self.mock_article = MagicMock()
        self.mock_article.id = "article123"
        self.progress = ArticleProductionProgress(article=self.mock_article)

    @patch('core.models.progress.ArticleService')
    def test_start_stage(self, mock_article_service):
        """测试开始阶段"""
        # 设置模拟行为
        mock_article_service.update_article_status.return_value = True

        # 调用被测方法
        self.progress.start_stage(ProductionStage.TOPIC_RESEARCH, 5)

        # 验证结果
        assert self.progress.current_stage == ProductionStage.TOPIC_RESEARCH
        assert self.progress.stages[ProductionStage.TOPIC_RESEARCH]["status"] == StageStatus.IN_PROGRESS
        assert self.progress.stages[ProductionStage.TOPIC_RESEARCH]["total_items"] == 5
        assert self.progress.stages[ProductionStage.TOPIC_RESEARCH]["start_time"] is not None
        mock_article_service.update_article_status.assert_called_once()

    def test_update_progress(self):
        """测试更新进度"""
        # 先开始阶段
        with patch('core.models.progress.ArticleService'):
            self.progress.start_stage(ProductionStage.TOPIC_RESEARCH, 10)

        # 调用被测方法
        self.progress.update_progress(
            stage=ProductionStage.TOPIC_RESEARCH,
            completed_items=5,
            avg_score=0.8,
            error_count=1
        )

        # 验证结果
        stage_progress = self.progress.stages[ProductionStage.TOPIC_RESEARCH]
        assert stage_progress["completed_items"] == 5
        assert stage_progress["avg_score"] == 0.8
        assert stage_progress["error_count"] == 1
        assert self.progress.error_count == 1

    @patch('core.models.progress.ArticleService')
    def test_complete_stage(self, mock_article_service):
        """测试完成阶段"""
        # 先开始阶段
        mock_article_service.update_article_status.return_value = True
        self.progress.start_stage(ProductionStage.TOPIC_DISCOVERY, 3)

        # 调用被测方法
        self.progress.complete_stage(ProductionStage.TOPIC_DISCOVERY)

        # 验证结果
        assert self.progress.stages[ProductionStage.TOPIC_DISCOVERY]["status"] == StageStatus.COMPLETED
        assert self.progress.stages[ProductionStage.TOPIC_DISCOVERY]["end_time"] is not None

        # 验证是否正确设置了下一阶段
        assert self.progress.current_stage == ProductionStage.TOPIC_RESEARCH
        assert self.progress.stages[ProductionStage.TOPIC_RESEARCH]["status"] == StageStatus.PENDING

        # 验证是否调用了文章状态更新
        assert mock_article_service.update_article_status.call_count == 2

    @patch('core.models.progress.ArticleService')
    def test_complete(self, mock_article_service):
        """测试完成整个生产流程"""
        # 设置模拟行为
        mock_article_service.update_article_status.return_value = True

        # 调用被测方法
        self.progress.complete()

        # 验证结果
        assert self.progress.current_stage == ProductionStage.COMPLETED
        assert self.progress.stages[ProductionStage.COMPLETED]["status"] == StageStatus.COMPLETED
        assert self.progress.completed_at is not None
        mock_article_service.update_article_status.assert_called_once_with(self.mock_article, "completed")

    @patch('core.models.progress.ArticleService')
    def test_fail(self, mock_article_service):
        """测试生产流程失败"""
        # 设置模拟行为
        mock_article_service.update_article_status.return_value = True

        # 调用被测方法
        self.progress.fail()

        # 验证结果
        assert self.progress.current_stage == ProductionStage.FAILED
        assert self.progress.stages[ProductionStage.FAILED]["status"] == StageStatus.FAILED
        assert self.progress.completed_at is not None
        mock_article_service.update_article_status.assert_called_once_with(self.mock_article, "failed")

    @patch('core.models.progress.ArticleService')
    def test_pause(self, mock_article_service):
        """测试暂停生产流程"""
        # 设置模拟行为
        mock_article_service.update_article_status.return_value = True

        # 先开始一个阶段
        self.progress.start_stage(ProductionStage.TOPIC_RESEARCH, 5)

        # 调用被测方法
        self.progress.pause()

        # 验证结果
        assert self.progress.current_stage == ProductionStage.PAUSED
        assert self.progress.stages[ProductionStage.PAUSED]["status"] == StageStatus.PAUSED
        assert self.progress.stages[ProductionStage.TOPIC_RESEARCH]["status"] == StageStatus.PAUSED
        mock_article_service.update_article_status.assert_called_with(self.mock_article, "paused")

    @patch('core.models.progress.ArticleService')
    def test_resume(self, mock_article_service):
        """测试恢复生产流程"""
        # 设置模拟行为
        mock_article_service.update_article_status.return_value = True

        # 先暂停流程
        self.progress.start_stage(ProductionStage.TOPIC_RESEARCH, 5)
        self.progress.pause()

        # 重置mock以便验证
        mock_article_service.reset_mock()

        # 调用被测方法
        self.progress.resume()

        # 验证结果
        assert self.progress.current_stage == ProductionStage.TOPIC_RESEARCH
        assert self.progress.stages[ProductionStage.TOPIC_RESEARCH]["status"] == StageStatus.IN_PROGRESS
        mock_article_service.update_article_status.assert_called_once()

    def test_add_error(self):
        """测试添加错误日志"""
        # 调用被测方法
        self.progress.add_error(ProductionStage.TOPIC_RESEARCH, "测试错误")

        # 验证结果
        assert len(self.progress.stage_history) == 1
        error_entry = self.progress.stage_history[0]
        assert error_entry["stage"] == ProductionStage.TOPIC_RESEARCH
        assert error_entry["error"] == "测试错误"
        assert "time" in error_entry

class TestArticleProductionProgressCalculations:
    """测试ArticleProductionProgress的计算功能"""

    def setup_method(self):
        """每个测试方法前的设置"""
        self.progress = ArticleProductionProgress(article_id="article123")
        # 设置开始时间为一小时前
        self.progress.started_at = datetime.now() - timedelta(hours=1)

    def test_duration(self):
        """测试计算持续时间"""
        # 验证结果 - 应该接近3600秒（1小时）
        duration = self.progress.duration
        assert 3590 <= duration <= 3610  # 允许几秒误差

    def test_duration_with_completion(self):
        """测试计算已完成任务的持续时间"""
        # 设置结束时间为开始后30分钟
        self.progress.completed_at = self.progress.started_at + timedelta(minutes=30)

        # 验证结果 - 应该接近1800秒（30分钟）
        assert self.progress.duration == 1800

    def test_progress_percentage(self):
        """测试计算进度百分比"""
        # 准备数据 - 只完成第一阶段
        self.progress.stages[ProductionStage.TOPIC_DISCOVERY]["status"] = StageStatus.COMPLETED
        self.progress.stages[ProductionStage.TOPIC_DISCOVERY]["completed_items"] = 5
        self.progress.stages[ProductionStage.TOPIC_DISCOVERY]["total_items"] = 5

        # 验证结果 - 第一阶段权重为0.1，所以总进度应为10%
        assert self.progress.progress_percentage == 10.0

    def test_progress_percentage_partial(self):
        """测试计算部分完成的进度百分比"""
        # 准备数据 - 第一阶段完成，第二阶段部分完成
        self.progress.stages[ProductionStage.TOPIC_DISCOVERY]["status"] = StageStatus.COMPLETED
        self.progress.stages[ProductionStage.TOPIC_DISCOVERY]["completed_items"] = 5
        self.progress.stages[ProductionStage.TOPIC_DISCOVERY]["total_items"] = 5

        self.progress.stages[ProductionStage.TOPIC_RESEARCH]["status"] = StageStatus.IN_PROGRESS
        self.progress.stages[ProductionStage.TOPIC_RESEARCH]["completed_items"] = 5
        self.progress.stages[ProductionStage.TOPIC_RESEARCH]["total_items"] = 10

        # 验证结果 - 第一阶段10% + 第二阶段(0.5 * 20%) = 10% + 10% = 20%
        assert self.progress.progress_percentage == 20.0

    def test_get_summary(self):
        """测试获取进度摘要"""
        # 准备数据
        self.progress.current_stage = ProductionStage.TOPIC_RESEARCH
        self.progress.stages[ProductionStage.TOPIC_RESEARCH]["status"] = StageStatus.IN_PROGRESS
        self.progress.add_error(ProductionStage.TOPIC_DISCOVERY, "测试错误")

        # 调用被测方法
        summary = self.progress.get_summary()

        # 验证结果
        assert summary["article_id"] == "article123"
        assert summary["current_stage"] == "topic_research"
        assert summary["stage_status"] == "in_progress"
        assert "progress_percentage" in summary
        assert "duration" in summary
        assert len(summary["stage_history"]) == 1
        assert len(summary["stages"]) == len(ProductionStage)
