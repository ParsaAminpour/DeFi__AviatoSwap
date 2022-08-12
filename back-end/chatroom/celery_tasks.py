from celery import shared_task

@shared_task
def sync_redis_with_db():
    pass