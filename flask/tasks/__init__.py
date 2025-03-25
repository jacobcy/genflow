from celery import Celery

def create_celery():
    """创建 Celery 实例"""
    celery = Celery(
        'genflow',
        broker='redis://localhost:6379/0',
        backend='redis://localhost:6379/0'
    )
    
    # 从环境变量加载配置
    celery.conf.update({
        'broker_url': celery.conf.broker_url,
        'result_backend': celery.conf.result_backend,
        'task_serializer': 'json',
        'result_serializer': 'json',
        'accept_content': ['json'],
        'broker_connection_retry_on_startup': True,
        # 防止重复节点名称
        'worker_deduplicate_successful_tasks': True,
        'worker_max_tasks_per_child': 1000,
        'worker_prefetch_multiplier': 1
    })
    
    return celery

# 创建 celery 实例
celery = create_celery()

# 导入任务
from . import article_tasks
