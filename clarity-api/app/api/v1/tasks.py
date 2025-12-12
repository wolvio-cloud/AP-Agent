"""
Task Status and Monitoring API Endpoints

Provides endpoints to check status of background tasks.
"""

from fastapi import APIRouter, HTTPException, Depends
from app.celery_app import celery_app
from app.core.deps import get_current_active_user
from app.models.user import User
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/tasks/{task_id}/status")
async def get_task_status(
    task_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get status of background task

    Args:
        task_id: Celery task ID

    Returns:
        Task status and result/error information
    """
    task = celery_app.AsyncResult(task_id)

    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'Pending...',
            'progress': 0
        }
    elif task.state == 'PROCESSING':
        meta = task.info or {}
        response = {
            'state': task.state,
            'status': meta.get('status', 'Processing...'),
            'progress': meta.get('progress', 50),
            'current': meta.get('current'),
            'total': meta.get('total')
        }
    elif task.state == 'SUCCESS':
        response = {
            'state': task.state,
            'status': 'Completed',
            'progress': 100,
            'result': task.result
        }
    elif task.state == 'FAILURE':
        response = {
            'state': task.state,
            'status': 'Failed',
            'progress': 0,
            'error': str(task.info) if task.info else 'Unknown error'
        }
    elif task.state == 'RETRY':
        response = {
            'state': task.state,
            'status': 'Retrying...',
            'progress': 25
        }
    else:
        response = {
            'state': task.state,
            'status': task.state,
            'progress': 0
        }

    return response


@router.get("/tasks/stats")
async def get_task_stats(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get Celery worker statistics

    Returns:
        Statistics about active, scheduled, and reserved tasks
    """
    try:
        inspect = celery_app.control.inspect()

        stats = {
            'active': inspect.active() or {},
            'scheduled': inspect.scheduled() or {},
            'reserved': inspect.reserved() or {},
            'registered': list(inspect.registered().values())[0] if inspect.registered() else []
        }

        # Count total tasks
        total_active = sum(len(tasks) for tasks in stats['active'].values())
        total_scheduled = sum(len(tasks) for tasks in stats['scheduled'].values())
        total_reserved = sum(len(tasks) for tasks in stats['reserved'].values())

        return {
            'totals': {
                'active': total_active,
                'scheduled': total_scheduled,
                'reserved': total_reserved
            },
            'details': stats
        }

    except Exception as e:
        logger.error(f"Failed to get task stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve task statistics")


@router.get("/tasks/queues")
async def get_queue_lengths(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get length of each task queue

    Returns:
        Number of tasks in each queue
    """
    try:
        inspect = celery_app.control.inspect()

        # Get active queue lengths
        active = inspect.active_queues()

        if not active:
            return {
                'extraction': 0,
                'validation': 0,
                'notifications': 0,
                'exports': 0,
                'analytics': 0
            }

        # Sum up tasks across workers
        queue_counts = {}
        for worker, queues in active.items():
            for queue_info in queues:
                queue_name = queue_info['name']
                queue_counts[queue_name] = queue_counts.get(queue_name, 0) + 1

        return queue_counts

    except Exception as e:
        logger.error(f"Failed to get queue lengths: {e}")
        return {
            'extraction': 0,
            'validation': 0,
            'notifications': 0,
            'exports': 0,
            'analytics': 0
        }


@router.post("/tasks/{task_id}/cancel")
async def cancel_task(
    task_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Cancel a running task

    Args:
        task_id: Celery task ID

    Returns:
        Cancellation status
    """
    try:
        celery_app.control.revoke(task_id, terminate=True)

        return {
            'message': 'Task cancellation requested',
            'task_id': task_id
        }

    except Exception as e:
        logger.error(f"Failed to cancel task {task_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to cancel task")


@router.get("/tasks/active")
async def get_active_tasks(
    current_user: User = Depends(get_current_active_user),
    queue: Optional[str] = None
):
    """
    Get list of currently active tasks

    Args:
        queue: Optional queue name to filter by

    Returns:
        List of active tasks
    """
    try:
        inspect = celery_app.control.inspect()
        active = inspect.active() or {}

        all_tasks = []
        for worker, tasks in active.items():
            for task in tasks:
                if queue is None or task.get('delivery_info', {}).get('routing_key') == queue:
                    all_tasks.append({
                        'id': task['id'],
                        'name': task['name'],
                        'args': task.get('args', []),
                        'worker': worker,
                        'queue': task.get('delivery_info', {}).get('routing_key')
                    })

        return {
            'count': len(all_tasks),
            'tasks': all_tasks
        }

    except Exception as e:
        logger.error(f"Failed to get active tasks: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve active tasks")
