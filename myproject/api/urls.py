from django.urls import path
from .views import hello_world
from .views_auth import register, login
from .views_gmail import gmail_auth_url, gmail_callback, gmail_receipts, sync_emails, get_user_emails, get_email_detail

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
]
