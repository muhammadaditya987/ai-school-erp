from celery import Celery

from app.core.config import get_settings

settings = get_settings()
celery_app = Celery(
    "school_erp",
    broker=settings.rabbitmq_url,
    backend=settings.redis_url,
    include=["app.tasks"],
)
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    result_expires=3600,
    broker_connection_retry_on_startup=True,
)
