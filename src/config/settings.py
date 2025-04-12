import os
from pathlib import Path

# redis configs
# REDIS_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
REDIS_BROKER_URL = "redis://localhost:6379/0"
# Celery configs
CELERY_BROKER_POOL_LIMIT = 20
CELERY_BROKER_CONNECTION_TIMEOUT = 30
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

# LLM default configs
LLM_BASE_URL = "http://localhost:11434"
LLM_API_KEY = "ollama"
LLM_MODEL = "qwen2.5:0.5b"

# sqlite path
DATABASE_PATH = "market-flow.db"

# logging config
LOG_DIR = os.getenv("LOG_DIR", str(Path(__file__).parent.parent / "logs"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

