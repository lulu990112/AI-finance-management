
import os
import requests
from django.conf import settings
from django.shortcuts import redirect
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, LoginSerializer

@api_view(['POST'])
def register(request):
    # 先检查用户名和邮箱是否已存在
    username = request.data.get('username')
    email = request.data.get('email')
    if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
        return Response({
            "success": False,
            "message": "用户名或邮箱已被占用",
            "error_code": "USER_ALREADY_EXISTS"
        }, status=status.HTTP_409_CONFLICT)

    # 正常校验和保存
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        # 新增：注册成功后直接生成token
        refresh = RefreshToken.for_user(user)
        token = str(refresh.access_token)
        return Response({
            "success": True,
            "message": "用户注册成功",
            "data": {
                "token": token,
                "user": {
                    "userid": user.id,
                    "username": user.username,
                    "email": user.email,
                    "createdAt": user.date_joined.replace(microsecond=0).isoformat() + 'Z',
                }
            }
        }, status=status.HTTP_201_CREATED)
    else:
        errors = serializer.errors
        error_code = "VALIDATION_FAILED"
        return Response({
            "success": False,
            "message": "请求参数验证失败，请检查提交的数据。",
            "error_code": error_code,
            "errors": errors
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({
            "success": False,
            "message": "请求参数验证失败，请检查提交的数据。",
            "error_code": "VALIDATION_FAILED",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    username = serializer.validated_data['username']
    password = serializer.validated_data['password']

    user = authenticate(username=username, password=password)
    if user is None:
        return Response({
            "success": False,
            "message": "用户名或密码错误。",
            "error_code": "INVALID_CREDENTIALS"
        }, status=status.HTTP_401_UNAUTHORIZED)

    try:
        refresh = RefreshToken.for_user(user)
        token = str(refresh.access_token)
    except Exception:
        token = None

    # 判断是否为会员
    is_Member = user.groups.filter(name="Member").exists()

    return Response({
        "success": True,
        "message": "登录成功",
        "data": {
            "token": token,
            "user": {
                "userid": user.id,
                "username": user.username,
                "email": user.email,
                "isMember": is_Member,
            }
        }
    }, status=status.HTTP_200_OK)


