import os
from src.config.settings import *
from celery import Celery

app = Celery('market_flow')
app.conf.update(
    broker_url=REDIS_BROKER_URL,
    # result_backend=result_backend,
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    task_time_limit=300,
    # task_soft_time_limit=60,
    # task_default_retry_delay=60,
    # task_max_retries=3,
    # worker_send_task_events=True,
    # worker_prefetch_multiplier=1,
    imports=['src.tasks.market_tasks'],
    task_routes={
        'execute_market_flow': {'queue': 'market_flow'},
    }
)

# expose celery_app for import in other modules
__all__ = ['app']
