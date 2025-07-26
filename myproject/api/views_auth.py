
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

# 1. 生成 Gmail 授权链接
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def gmail_auth_url(request):
    import urllib.parse
    params = {
        'client_id': settings.GOOGLE_CLIENT_ID,
        'redirect_uri': settings.GOOGLE_REDIRECT_URI,
        'response_type': 'code',
        'scope': ' '.join(settings.GOOGLE_SCOPES),
        'access_type': 'offline',
        'prompt': 'consent',
        'state': str(request.user.id),  # 用 user id 作为 state
    }
    url = 'https://accounts.google.com/o/oauth2/v2/auth?' + urllib.parse.urlencode(params)
    return Response({'auth_url': url})

# 2. Gmail 授权回调，获取 access_token 并保存
@api_view(['GET'])
@permission_classes([AllowAny])  # 允许任何人访问
def gmail_callback(request):
    code = request.GET.get('code')
    state = request.GET.get('state')  # 这里拿到 user_id
    if not code:
        return Response({'error': 'No code provided'}, status=400)
    data = {
        'code': code,
        'client_id': settings.GOOGLE_CLIENT_ID,
        'client_secret': settings.GOOGLE_CLIENT_SECRET,
        'redirect_uri': settings.GOOGLE_REDIRECT_URI,
        'grant_type': 'authorization_code',
    }
    token_url = 'https://oauth2.googleapis.com/token'
    r = requests.post(token_url, data=data)
    if r.status_code != 200:
        return Response({'error': 'Failed to get token', 'details': r.json()}, status=400)
    token_info = r.json()
    access_token = token_info.get('access_token')
    if not access_token:
        return Response({'error': 'No access_token in response', 'details': token_info}, status=400)
    # 你可以在这里用 state(user_id) 做用户绑定或存储
    redirect_url = f"http://localhost:3000/gmail-success?access_token={access_token}"
    return redirect(redirect_url)

# 3. 用 access_token 拉取 Gmail 收据（示例：拉取最近10封邮件）
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def gmail_receipts(request):
    access_token = request.GET.get('access_token')  # 实际应从数据库获取
    if not access_token:
        return Response({'error': 'No access_token provided'}, status=400)
    headers = {'Authorization': f'Bearer {access_token}'}
    gmail_api = 'https://gmail.googleapis.com/gmail/v1/users/me/messages'
    params = {'maxResults': 10}
    r = requests.get(gmail_api, headers=headers, params=params)
    if r.status_code != 200:
        return Response({'error': 'Failed to fetch emails', 'details': r.json()}, status=400)
    return Response(r.json())
