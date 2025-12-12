"""
Celery Application for Background Task Processing

This module configures Celery for asynchronous invoice processing,
validation, notifications, and exports.
"""

from celery import Celery
import os

# Initialize Celery
celery_app = Celery(
    'clarity',
    broker=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('REDIS_URL', 'redis://localhost:6379/0')
)

# Configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max per task
    task_soft_time_limit=240,  # 4 minute warning
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,

    # Task result expiration
    result_expires=3600,  # Results expire after 1 hour

    # Retry configuration
    task_acks_late=True,  # Acknowledge task after completion
    task_reject_on_worker_lost=True,
)

# Task routing - different queues for different priorities
celery_app.conf.task_routes = {
    'app.tasks.extraction.*': {'queue': 'extraction'},
    'app.tasks.validation.*': {'queue': 'validation'},
    'app.tasks.notifications.*': {'queue': 'notifications'},
    'app.tasks.exports.*': {'queue': 'exports'},
    'app.tasks.analytics.*': {'queue': 'analytics'},
}

# Auto-discover tasks in these modules
celery_app.autodiscover_tasks(['app.tasks'])

# Celery Beat schedule (periodic tasks)
celery_app.conf.beat_schedule = {
    'check-overdue-approvals': {
        'task': 'app.tasks.approval_tasks.check_overdue_approvals',
        'schedule': 3600.0,  # Every hour
    },
    'cleanup-old-tasks': {
        'task': 'app.tasks.maintenance_tasks.cleanup_old_task_results',
        'schedule': 86400.0,  # Every 24 hours
    },
}
