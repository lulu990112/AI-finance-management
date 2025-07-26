from django.urls import path
from .views import hello_world
from .views_auth import register, login
from . import views_auth

urlpatterns = [
    path('hello/', hello_world),
    path('register/', register),
    path('login/', login),
    path('gmail/auth_url/', views_auth.gmail_auth_url, name='gmail_auth_url'),
    path('gmail/callback/', views_auth.gmail_callback, name='gmail_callback'),
    path('gmail/receipts/', views_auth.gmail_receipts, name='gmail_receipts'),
]
