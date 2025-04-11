from .app import celery_app

# expose celery_app for import in other modules
__all__ = ['celery_app']