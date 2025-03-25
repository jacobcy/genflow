from celery import Celery
from core.config import settings
from api.deps import get_redis_url

celery_app = Celery(
    "genflow",
    broker=get_redis_url(),
    backend=get_redis_url(),
    include=[
        "tasks",
        "core.tools.trending_tools.tasks"
    ]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
)

# 配置定时任务
celery_app.conf.beat_schedule = {
    'update-trending-data': {
        'task': 'core.tools.trending_tools.tasks.update_trending_data',
        'schedule': 60 * 60 * 3,  # 3小时执行一次
        'options': {
            'expires': 60 * 60 * 2  # 2小时后过期
        }
    }
}

# 自动发现任务
celery_app.autodiscover_tasks(
    ["src.core.tasks", "core.tools.trending_tools"],
    related_name="tasks",
    force=True
)
