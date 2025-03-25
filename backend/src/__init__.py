# 延迟导入避免启动时的循环导入问题
def get_celery_app():
    from .worker import celery_app
    return celery_app

__all__ = ("get_celery_app",)
