import os
import requests
import json
from django.conf import settings
from django.shortcuts import redirect
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework import status
from email.utils import parsedate_to_datetime
from django.utils import timezone
from datetime import timedelta
from .models import GmailToken, Email

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
    
    # 验证用户是否存在
    try:
        user = User.objects.get(id=int(state))
    except (ValueError, User.DoesNotExist):
        return Response({'error': 'Invalid user'}, status=400)
    
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
    
    # 保存token到数据库，与用户关联
    
    GmailToken.objects.update_or_create(
        user=user,
        defaults={
            'access_token': access_token,
            'refresh_token': token_info.get('refresh_token'),
            'expires_at': timezone.now() + timedelta(seconds=token_info.get('expires_in', 3600))
        }
    )
    
    redirect_url = f"http://localhost:3000/gmail-success?access_token={access_token}"
    return redirect(redirect_url)

# 3. 同步邮件到数据库
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sync_emails(request):
    user = request.user
    
    # 从数据库获取用户的Gmail token
    try:
        gmail_token = GmailToken.objects.get(user=user)
    except GmailToken.DoesNotExist:
        return Response({'error': 'No Gmail token found for this user'}, status=400)
    
    headers = {'Authorization': f'Bearer {gmail_token.access_token}'}
    gmail_api = 'https://gmail.googleapis.com/gmail/v1/users/me/messages'
    params = {'maxResults': 50}
    r = requests.get(gmail_api, headers=headers, params=params)
    if r.status_code != 200:
        return Response({'error': 'Failed to fetch emails', 'details': r.json()}, status=400)
    
    messages = r.json().get('messages', [])
    saved_emails = []
    
    # 保存邮件到数据库
    
    for msg in messages:
        # 获取邮件详细信息
        msg_detail = requests.get(
            f"{gmail_api}/{msg['id']}",
            headers=headers
        ).json()
        
        # 解析邮件头信息
        headers_dict = {h['name']: h['value'] for h in msg_detail.get('payload', {}).get('headers', [])}
        
        # 解析邮件时间
        try:
            received_at = parsedate_to_datetime(headers_dict.get('Date', ''))
        except:
            received_at = timezone.now()
        
        # 保存到数据库
        email_obj, created = Email.objects.update_or_create(
            user=user,
            gmail_id=msg['id'],
            defaults={
                'thread_id': msg_detail.get('threadId', ''),
                'subject': headers_dict.get('Subject', ''),
                'sender': headers_dict.get('From', ''),
                'recipients': headers_dict.get('To', ''),
                'snippet': msg_detail.get('snippet', ''),
                'received_at': received_at,
                'labels': json.dumps(msg_detail.get('labelIds', [])),
                'is_read': 'UNREAD' not in msg_detail.get('labelIds', [])
            }
        )
        
        saved_emails.append({
            'id': email_obj.id,
            'subject': email_obj.subject,
            'sender': email_obj.sender,
            'snippet': email_obj.snippet,
            'received_at': email_obj.received_at.isoformat(),
            'is_read': email_obj.is_read,
            'created': created
        })
    
    return Response({
        'message': f'Successfully synced {len(saved_emails)} emails',
        'emails': saved_emails,
        'user': user.username
    })

# 4. 查看用户的邮件列表
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_emails(request):
    user = request.user
    
    # 获取查询参数
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 20))
    is_read = request.GET.get('is_read')
    
    # 构建查询
    emails = Email.objects.filter(user=user)
    
    if is_read is not None:
        emails = emails.filter(is_read=is_read.lower() == 'true')
    
    # 按时间倒序排列
    emails = emails.order_by('-received_at')
    
    # 分页
    start = (page - 1) * page_size
    end = start + page_size
    
    email_list = []
    for email in emails[start:end]:
        email_list.append({
            'id': email.id,
            'gmail_id': email.gmail_id,
            'subject': email.subject,
            'sender': email.sender,
            'snippet': email.snippet,
            'received_at': email.received_at.isoformat(),
            'is_read': email.is_read,
            'labels': email.get_labels_list()
        })
    
    return Response({
        'emails': email_list,
        'total': emails.count(),
        'page': page,
        'page_size': page_size,
        'user': user.username
    })

# 5. 获取单个邮件的详细信息
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_email_detail(request, email_id):
    user = request.user
    
    try:
        email = Email.objects.get(id=email_id, user=user)
    except Email.DoesNotExist:
        return Response({'error': 'Email not found'}, status=404)
    
    return Response({
        'id': email.id,
        'gmail_id': email.gmail_id,
        'thread_id': email.thread_id,
        'subject': email.subject,
        'sender': email.sender,
        'recipients': email.get_recipients_list(),
        'body': email.body,
        'snippet': email.snippet,
        'received_at': email.received_at.isoformat(),
        'is_read': email.is_read,
        'labels': email.get_labels_list(),
        'created_at': email.created_at.isoformat()
    })

# 6. 保持原有的gmail_receipts函数（向后兼容）
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def gmail_receipts(request):
    """保持原有API兼容性，直接调用sync_emails"""
    return sync_emails(request) 