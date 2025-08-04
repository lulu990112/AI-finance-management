from django.urls import path
from .views import hello_world
from .views_auth import register, login
from .views_gmail import gmail_auth_url, gmail_callback, gmail_receipts, sync_emails, get_user_emails, get_email_detail
from .views_gpt import get_unprocessed_emails, get_categories, get_transactions, get_processing_stats, batch_sync_and_process_emails

urlpatterns = [
    path('hello/', hello_world),
    path('register/', register),
    path('login/', login),
    # Gmail相关路由
    path('gmail/auth_url/', gmail_auth_url, name='gmail_auth_url'),
    path('gmail/callback/', gmail_callback, name='gmail_callback'),
    path('gmail/receipts/', gmail_receipts, name='gmail_receipts'),
    path('gmail/sync/', sync_emails, name='sync_emails'),
    path('gmail/emails/', get_user_emails, name='get_user_emails'),
    path('gmail/emails/<int:email_id>/', get_email_detail, name='get_email_detail'),
    # GPT相关路由
    path('gpt/unprocessed_emails/', get_unprocessed_emails, name='get_unprocessed_emails'),
    path('gpt/categories/', get_categories, name='get_categories'),
    path('gpt/transactions/', get_transactions, name='get_transactions'),
    # 批量处理相关路由
    path('gpt/processing_stats/', get_processing_stats, name='get_processing_stats'),
    # 批量同步和处理邮件
    path('gpt/batch_sync_and_process/', batch_sync_and_process_emails, name='batch_sync_and_process_emails'),
]
