#!/usr/bin/env python
"""
Celery monitoring script
Used to check Celery service status and task execution
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Set Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from celery import current_app
from api.tasks import daily_gmail_sync_task
from django.contrib.auth.models import User
from api.models import GmailToken, Email, Transaction

def check_celery_status():
    """Check Celery service status"""
    try:
        # Check worker status
        inspect = current_app.control.inspect()
        active_workers = inspect.active()
        registered_tasks = inspect.registered()
        
        print("=" * 50)
        print("Celery service status check")
        print("=" * 50)
        
        if active_workers:
            print(f"Active Worker count: {len(active_workers)}")
            for worker, tasks in active_workers.items():
                print(f"   Worker: {worker}")
                print(f"   Active tasks: {len(tasks)}")
        else:
            print("No active workers")
        
        if registered_tasks:
            print(f"Registered tasks count: {len(registered_tasks)}")
            for worker, tasks in registered_tasks.items():
                print(f"   Worker: {worker}")
                print(f"   Tasks: {', '.join(tasks)}")
        else:
            print("No registered tasks")
            
    except Exception as e:
        print(f"Check Celery status failed: {e}")

def check_scheduled_tasks():
    """Check scheduled task configuration"""
    try:
        from django_celery_beat.models import PeriodicTask
        
        print("\n" + "=" * 50)
        print("Scheduled task configuration check")
        print("=" * 50)
        
        tasks = PeriodicTask.objects.all()
        if tasks:
            for task in tasks:
                print(f"Task name: {task.name}")
                print(f"Task function: {task.task}")
                print(f"Schedule: {task.interval}")
                print(f"Enabled status: {'Yes' if task.enabled else 'No'}")
                print(f"Last run: {task.last_run_at}")
                print("-" * 30)
        else:
            print("No scheduled tasks configured")
            
    except ImportError:
        print("django-celery-beat not installed")
    except Exception as e:
        print(f"Check scheduled task failed: {e}")

def check_user_data():
    """Check user data status"""
    try:
        print("\n" + "=" * 50)
        print("User data status check")
        print("=" * 50)
        
        total_users = User.objects.count()
        users_with_gmail = GmailToken.objects.count()
        total_emails = Email.objects.count()
        unprocessed_emails = Email.objects.filter(is_processed=False).count()
        total_transactions = Transaction.objects.count()
        
        print(f"Total users: {total_users}")
        print(f"Users with Gmail Token: {users_with_gmail}")
        print(f"Total emails: {total_emails}")
        print(f"Unprocessed emails: {unprocessed_emails}")
        print(f"Total transactions: {total_transactions}")
        
        # Check recent 24 hours emails
        yesterday = datetime.now() - timedelta(days=1)
        recent_emails = Email.objects.filter(created_at__gte=yesterday).count()
        print(f"Recent 24 hours new emails: {recent_emails}")
        
    except Exception as e:
        print(f"Check user data failed: {e}")

def test_task_execution():
    """Test task execution (placeholder after removing health_check_task)"""  
    try:
        print("\n" + "=" * 50)
        print("Task execution test")
        print("=" * 50)
        print("health_check_task has been removed; no direct task invocation here.")
    except Exception as e:
        print(f"Test task execution failed: {e}")

def main():
    """Main function"""
    print("Celery monitoring script started...")
    print(f"Current time: {datetime.now()}")
    
    check_celery_status()
    check_scheduled_tasks()
    check_user_data()
    test_task_execution()
    
    print("\n" + "=" * 50)
    print("Monitoring check completed")
    print("=" * 50)

if __name__ == "__main__":
    main()






