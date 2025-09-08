from django.urls import path
from .views import hello_world
from .views_auth import register, login
from .views_gmail import gmail_auth_url, gmail_callback, gmail_receipts, sync_emails, get_user_emails, get_email_detail, check_gmail_auth_status
from .views_gpt import get_unprocessed_emails, get_categories, get_transactions, get_processing_stats, batch_sync_and_process_emails
from .views_ai_report import get_ai_report_detail, get_ai_reports, get_latest_ai_report, get_biweekly_reports, get_latest_biweekly_report, get_biweekly_report_by_period, generate_biweekly_report
from .views_group import (
    create_group, get_user_groups, get_group_info, join_group, leave_group,
    share_transactions, get_group_transactions, add_manual_transaction,
    get_group_ai_reports, get_categories, get_subcategories,
    generate_group_ai_report, get_group_statistics, export_group_data
)

urlpatterns = [
    path('hello/', hello_world),
    path('register/', register),
    path('login/', login),
    # Gmail related routes
    path('gmail/auth_url/', gmail_auth_url, name='gmail_auth_url'),
    path('gmail/callback/', gmail_callback, name='gmail_callback'),
    path('gmail/receipts/', gmail_receipts, name='gmail_receipts'),
    path('gmail/sync/', sync_emails, name='sync_emails'),
    path('gmail/emails/', get_user_emails, name='get_user_emails'),
    path('gmail/emails/<int:email_id>/', get_email_detail, name='get_email_detail'),
    path('gmail/auth_status/', check_gmail_auth_status, name='check_gmail_auth_status'),
    # GPT related routes
    path('gpt/unprocessed_emails/', get_unprocessed_emails, name='get_unprocessed_emails'),
    path('gpt/categories/', get_categories, name='get_categories'),
    path('gpt/transactions/', get_transactions, name='get_transactions'),
    # Batch processing related routes
    path('gpt/processing_stats/', get_processing_stats, name='get_processing_stats'),
    # Batch sync and process emails
    path('gpt/batch_sync_and_process/', batch_sync_and_process_emails, name='batch_sync_and_process_emails'),
    # AI Report related routes
    path('ai_report/reports/<int:report_id>/', get_ai_report_detail, name='get_ai_report_detail'),
    path('ai_report/reports/', get_ai_reports, name='get_ai_reports'),
    path('ai_report/latest/', get_latest_ai_report, name='get_latest_ai_report'),
    # Biweekly report related routes
    path('ai_report/biweekly/', get_biweekly_reports, name='get_biweekly_reports'),
    path('ai_report/biweekly/latest/', get_latest_biweekly_report, name='get_latest_biweekly_report'),
    path('ai_report/biweekly/generate/', generate_biweekly_report, name='generate_biweekly_report'),
    path('ai_report/biweekly/<str:start_date>/<str:end_date>/', get_biweekly_report_by_period, name='get_biweekly_report_by_period'),
    # Group related routes
    path('group/create/', create_group, name='create_group'),
    path('group/list/', get_user_groups, name='get_user_groups'),
    path('group/<int:group_id>/', get_group_info, name='get_group_info'),
    path('group/join/', join_group, name='join_group'),
    path('group/<int:group_id>/leave/', leave_group, name='leave_group'),
    path('group/share_transactions/', share_transactions, name='share_transactions'),
    path('group/<int:group_id>/transactions/', get_group_transactions, name='get_group_transactions'),
    path('group/<int:group_id>/transactions/add/', add_manual_transaction, name='add_manual_transaction'),
    path('group/<int:group_id>/ai_reports/', get_group_ai_reports, name='get_group_ai_reports'),
    path('group/<int:group_id>/ai_reports/generate/', generate_group_ai_report, name='generate_group_ai_report'),
    path('group/<int:group_id>/statistics/', get_group_statistics, name='get_group_statistics'),
    path('group/<int:group_id>/export/', export_group_data, name='export_group_data'),
    path('group/categories/', get_categories, name='get_group_categories'),
    path('group/categories/<int:category_id>/subcategories/', get_subcategories, name='get_subcategories'),
]
