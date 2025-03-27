import asyncio
from core.controllers.crewai_sequential_controller import CrewAISequentialController
from core.controllers.crewai_hierarchical_controller import CrewAIManagerController
from core.models.article import Article

async def test_sequential():
    # 创建文章对象
    article = Article(id='test-article', title='测试文章', status='draft')

    # 创建控制器
    controller = CrewAISequentialController(model_name='gpt-3.5-turbo')

    # 初始化控制器
    await controller.initialize()

    # 获取初始状态
    print('初始状态:', controller.state.status)

    # 测试状态标记方法
    controller.state.mark_start()
    print('开始后状态:', controller.state.status)

    controller.state.mark_complete()
    print('完成后状态:', controller.state.status)

    # 测试取消功能
    result = controller.cancel_production()
    print('取消结果:', result)
    print('取消后状态:', controller.state.status)

    # 测试文章集成
    controller.state.article = article
    controller.state.mark_failed('测试错误')
    print('文章状态:', article.status)

async def test_hierarchical():
    # 创建文章对象
    article = Article(id='test-article-h', title='层次流程测试文章', status='draft')

    # 创建控制器
    controller = CrewAIManagerController(model_name='gpt-3.5-turbo')

    # 初始化控制器
    await controller.initialize()

    # 获取初始状态
    print('\n层次流程初始状态:', controller.state.status)

    # 测试任务结果添加
    controller.state.add_task_result('研究任务', '这是研究结果')
    controller.state.add_delegated_task('委派任务1')

    # 输出测试结果
    print('任务结果:', controller.state.task_results)
    print('已完成任务:', controller.state.tasks_completed)
    print('委派任务:', controller.state.delegated_tasks)

    # 测试文章集成
    controller.state.article = article
    controller.state.mark_start()
    print('文章开始状态:', article.status)

    controller.state.mark_complete()
    print('文章完成状态:', article.status)

async def main():
    print("=== 测试顺序流程控制器 ===")
    await test_sequential()

    print("\n=== 测试层次流程控制器 ===")
    await test_hierarchical()

if __name__ == "__main__":
    asyncio.run(main())
