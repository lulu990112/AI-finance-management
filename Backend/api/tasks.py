"""
tasks.py

This module defines Celery tasks for scheduled operations such as daily Gmail
sync and generating biweekly AI reports.

Main methods:
- daily_gmail_sync_task
- create_system_token
- auto_generate_biweekly_ai_reports
"""

from celery import shared_task
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
import requests
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

@shared_task
def daily_gmail_sync_task():
    """
    Daily Gmail sync task executed at 00:00
    """
    logger.info("Starting daily Gmail sync task")
    
    try:
        # Get all users with Gmail token
        users_with_token = User.objects.filter(gmailtoken__isnull=False).distinct()
        
        if not users_with_token:
            logger.info("No users with Gmail token found")
            return
        
        total_synced = 0
        total_processed = 0
        total_transactions = 0
        
        for user in users_with_token:
            try:
                logger.info(f"Processing user: {user.username}")
                
                # Create JWT token for system task
                system_token = create_system_token(user)
                
                # Call batch_sync_and_process API
                response = requests.post(
                    'http://localhost:8000/api/gpt/batch_sync_and_process/',
                    json={
                        'max_sync_emails': 100,  # Maximum 100 emails per sync
                        'max_process_emails': 50,  # Maximum 50 emails per process
                        'auto_process': True
                    },
                    headers={
                        'Authorization': f'Bearer {system_token}',
                        'Content-Type': 'application/json'
                    },
                    timeout=300  # 5 minutes timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    user_synced = result.get('sync_stats', {}).get('total_synced', 0)
                    user_processed = result.get('process_results', {}).get('processed_count', 0)
                    user_transactions = result.get('process_results', {}).get('transactions_created', 0)
                    
                    total_synced += user_synced
                    total_processed += user_processed
                    total_transactions += user_transactions
                    
                    logger.info(f"User {user.username} sync completed: synced {user_synced} emails, processed {user_processed} emails, created {user_transactions} transactions")
                else:
                    logger.error(f"User {user.username} sync failed: {response.status_code} - {response.text}")
                    
            except Exception as e:
                logger.error(f"Error processing user {user.username}: {str(e)}")
                continue
        
        # Record task execution result
        task_result = {
            'task_name': 'daily_gmail_sync_task',
            'execution_time': timezone.now().isoformat(),
            'total_users': len(users_with_token),
            'total_synced': total_synced,
            'total_processed': total_processed,
            'total_transactions': total_transactions,
            'status': 'completed'
        }
        
        logger.info(f"Daily Gmail sync task completed: total synced {total_synced} emails, processed {total_processed} emails, created {total_transactions} transactions")
        
        return task_result
        
    except Exception as e:
        logger.error(f"Daily Gmail sync task failed: {str(e)}")
        # Record failure information
        task_result = {
            'task_name': 'daily_gmail_sync_task',
            'execution_time': timezone.now().isoformat(),
            'error': str(e),
            'status': 'failed'
        }
        raise

def create_system_token(user):
    """
    Create JWT token for system task
    """
    try:
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)
    except Exception as e:
        logger.error(f"Failed to create system token: {str(e)}")
        # If JWT token creation fails, return None, caller needs to handle
        return None

@shared_task
def auto_generate_biweekly_ai_reports():
    """
    Automatic generation of individual AI reports
    Executed at 00:00 on the fifteenth day after the last day of the latest individual AI report generation
    """
    logger.info("Starting auto-generate individual AI report task")
    
    try:
        from api.models import AIReport, Transaction
        from api.ai_report_service import AIReportGenerator
        from datetime import date, timedelta
        
        # Get all users with transaction records
        users_with_transactions = User.objects.filter(transactions__isnull=False).distinct()
        
        if not users_with_transactions:
            logger.info("No users with transaction records found")
            return
        
        total_users = len(users_with_transactions)
        total_reports_generated = 0
        total_reports_skipped = 0
        total_reports_failed = 0
        
        generator = AIReportGenerator()
        
        for user in users_with_transactions:
            try:
                logger.info(f"Processing user: {user.username}")
                
                # Get user's latest AI report
                latest_report = AIReport.objects.filter(
                    user=user,
                    report_type='biweekly',
                    is_generated=True,
                    generation_status='completed'
                ).order_by('-report_period_end').first()
                
                if not latest_report or not latest_report.report_period_end:
                    logger.info(f"User {user.username} does not have a valid AI report, skipping")
                    total_reports_skipped += 1
                    continue
                
                # Calculate next report period
                last_report_end = latest_report.report_period_end
                next_report_start = last_report_end + timedelta(days=1)
                next_report_end = next_report_start + timedelta(days=13)  # 14 days period
                
                # Check if current date is the generation time
                current_date = timezone.now().date()
                expected_generation_date = last_report_end + timedelta(days=15)
                
                if current_date < expected_generation_date:
                    logger.info(f"User {user.username} next report generation date is {expected_generation_date}, current date {current_date}, skipping")
                    total_reports_skipped += 1
                    continue
                
                # Check if there is a report for this period
                existing_report = AIReport.objects.filter(
                    user=user,
                    report_type='biweekly',
                    report_period_start=next_report_start,
                    report_period_end=next_report_end
                ).first()
                
                if existing_report:
                    logger.info(f"用户 {user.username} 的 {next_report_start} 到 {next_report_end} 的报告已存在，跳过")
                    total_reports_skipped += 1
                    continue
                
                # Check if there is transaction data for this period
                transactions_count = Transaction.objects.filter(
                    user=user,
                    transaction_date__date__gte=next_report_start,
                    transaction_date__date__lte=next_report_end
                ).count()
                
                if transactions_count == 0:
                    logger.info(f"User {user.username} has no transaction data in {next_report_start} to {next_report_end}, skipping")
                    total_reports_skipped += 1
                    continue
                
                # Generate report
                logger.info(f"Generating report for user {user.username} from {next_report_start} to {next_report_end}")
                report = generator.generate_biweekly_report(user, next_report_start, next_report_end)
                
                if report and report.is_generated:
                    total_reports_generated += 1
                    logger.info(f"User {user.username} report generation successful")
                else:
                    total_reports_failed += 1
                    logger.error(f"User {user.username} report generation failed")
                    
            except Exception as e:
                total_reports_failed += 1
                logger.error(f"Error processing user {user.username}: {str(e)}")
                continue
        
        # Record task execution result
        task_result = {
            'task_name': 'auto_generate_biweekly_ai_reports',
            'execution_time': timezone.now().isoformat(),
            'total_users': total_users,
            'total_reports_generated': total_reports_generated,
            'total_reports_skipped': total_reports_skipped,
            'total_reports_failed': total_reports_failed,
            'status': 'completed'
        }
        
        logger.info(f"Auto-generate individual AI report task completed: processed {total_users} users, generated {total_reports_generated} reports, skipped {total_reports_skipped} reports, failed {total_reports_failed} reports")
        
        return task_result
        
    except Exception as e:
        logger.error(f"Auto-generate individual AI report task failed: {str(e)}")
        task_result = {
            'task_name': 'auto_generate_biweekly_ai_reports',
            'execution_time': timezone.now().isoformat(),
            'error': str(e),
            'status': 'failed'
        }
        raise

