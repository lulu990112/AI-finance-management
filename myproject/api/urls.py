from django.urls import path
from .views import hello_world
from .views_auth import register, login

urlpatterns = [
    path('hello/', hello_world),
    path('register/', register),
    path('login/', login),
]
