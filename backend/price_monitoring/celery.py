"""
Celery configuration for price_monitoring project.
"""
import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'price_monitoring.settings')

app = Celery('price_monitoring')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Windows-specific configuration
app.conf.update(
    worker_pool='solo',  # Use solo pool for Windows compatibility
    worker_concurrency=1,  # Single worker for Windows
    task_always_eager=False,  # Allow async tasks
    task_eager_propagates=True,
)

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
