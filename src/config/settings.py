# redis configs
REDIS_BROKER_URL = "redis://localhost:6379/0"

# Celery configs
CELERY_BROKER_POOL_LIMIT = 20
CELERY_BROKER_CONNECTION_TIMEOUT = 30
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

# LLM default configs
BASE_URL = "http://localhost:11434/v1"
API_KEY = "ollama"
MODEL = "qwen2.5:0.5b"

# sqlite path
DATABASE_PATH = "marketing.db"
