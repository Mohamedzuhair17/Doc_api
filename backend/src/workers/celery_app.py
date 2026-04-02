from celery import Celery
from src.core.config import settings

celery_app = Celery(
    "document_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.autodiscover_tasks(['src.workers'])
