import os
import requests
import json
import base64
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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def gmail_auth_url(request):
    """生成Gmail授权链接"""
    import urllib.parse
    params = {
        'client_id': settings.GOOGLE_CLIENT_ID,
        'redirect_uri': settings.GOOGLE_REDIRECT_URI,
        'response_type': 'code',
        'scope': ' '.join(settings.GOOGLE_SCOPES),
        'access_type': 'offline',
        'prompt': 'consent',
        'state': str(request.user.id),
    }
    url = 'https://accounts.google.com/o/oauth2/v2/auth?' + urllib.parse.urlencode(params)
    return Response({'auth_url': url})

@api_view(['GET'])
@permission_classes([AllowAny])
def gmail_callback(request):
    """Gmail授权回调"""
    code = request.GET.get('code')
    state = request.GET.get('state')
    if not code:
        return Response({'error': 'No code provided'}, status=400)
    
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
    
    # 保存token到数据库
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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sync_emails(request):
    """同步邮件到数据库 - 支持增量同步"""
    user = request.user
    auto_process = request.GET.get('auto_process', 'true').lower() == 'true'
    max_results = int(request.GET.get('max_results', 50))
    
    try:
        gmail_token = GmailToken.objects.get(user=user)
    except GmailToken.DoesNotExist:
        return Response({'error': 'No Gmail token found for this user'}, status=400)
    
    # 使用增量同步参数
    from .email_processing_utils import get_incremental_sync_params, update_sync_time
    params = get_incremental_sync_params(user, max_results)
    
    headers = {'Authorization': f'Bearer {gmail_token.access_token}'}
    gmail_api = 'https://gmail.googleapis.com/gmail/v1/users/me/messages'
    
    r = requests.get(gmail_api, headers=headers, params=params)
    if r.status_code != 200:
        return Response({'error': 'Failed to fetch emails', 'details': r.json()}, status=400)
    
    messages = r.json().get('messages', [])
    saved_emails = []
    newly_created_emails = []
    
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
        
        # 解析邮件正文（简化版本）
        body_text = ""
        payload = msg_detail.get('payload', {})
        if 'parts' in payload:
            for part in payload['parts']:
                if part.get('mimeType') == 'text/plain':
                    body_data = part.get('body', {}).get('data', '')
                    if body_data:
                        try:
                            body_text = base64.urlsafe_b64decode(body_data + '=' * (4 - len(body_data) % 4)).decode('utf-8')
                            break
                        except:
                            pass
        else:
            body_data = payload.get('body', {}).get('data', '')
            if body_data:
                try:
                    body_text = base64.urlsafe_b64decode(body_data + '=' * (4 - len(body_data) % 4)).decode('utf-8')
                except:
                    pass
        
        # 保存到数据库，包含同步时间
        email_obj, created = Email.objects.update_or_create(
            user=user,
            gmail_id=msg['id'],
            defaults={
                'thread_id': msg_detail.get('threadId', ''),
                'subject': headers_dict.get('Subject', ''),
                'sender': headers_dict.get('From', ''),
                'recipients': headers_dict.get('To', ''),
                'snippet': msg_detail.get('snippet', ''),
                'body': body_text,
                'received_at': received_at,
                'labels': json.dumps(msg_detail.get('labelIds', [])),
                'is_read': 'UNREAD' not in msg_detail.get('labelIds', []),
                'last_sync_time': timezone.now()  # 记录同步时间
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
        
        if created:
            newly_created_emails.append(email_obj)
    
    # 更新全局同步时间
    update_sync_time(user)
    
    # 自动处理邮件
    auto_process_result = None
    if auto_process and newly_created_emails:
        try:
            from .email_processing_utils import process_emails_batch
            auto_process_result = process_emails_batch(newly_created_emails, user)
        except Exception as e:
            print(f"自动处理邮件失败: {e}")
    
    response_data = {
        'message': f'Successfully synced {len(saved_emails)} emails',
        'emails': saved_emails,
        'user': user.username,
        'newly_created_count': len(newly_created_emails),
        'auto_process_enabled': auto_process
    }
    
    if auto_process_result:
        response_data['auto_process_result'] = auto_process_result
    
    return Response(response_data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_emails(request):
    """查看用户的邮件列表"""
    user = request.user
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 20))
    is_read = request.GET.get('is_read')
    
    emails = Email.objects.filter(user=user)
    
    if is_read is not None:
        emails = emails.filter(is_read=is_read.lower() == 'true')
    
    emails = emails.order_by('-received_at')
    
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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_email_detail(request, email_id):
    """获取单个邮件的详细信息"""
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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def gmail_receipts(request):
    """保持原有API兼容性"""
    return sync_emails(request) 

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_sync_stats(request):
    """获取同步统计信息"""
    user = request.user
    
    try:
        gmail_token = GmailToken.objects.get(user=user)
        
        # 获取统计信息
        total_emails = Email.objects.filter(user=user).count()
        processed_emails = Email.objects.filter(user=user, is_processed=True).count()
        unprocessed_emails = Email.objects.filter(user=user, is_processed=False).count()
        
        # 获取最近同步信息
        last_sync_time = gmail_token.last_sync_time
        sync_status = "已同步" if last_sync_time else "未同步"
        
        # 获取最近7天的同步统计
        from datetime import timedelta
        from django.utils import timezone
        
        seven_days_ago = timezone.now() - timedelta(days=7)
        recent_emails = Email.objects.filter(
            user=user,
            created_at__gte=seven_days_ago
        ).count()
        
        return Response({
            'sync_status': sync_status,
            'last_sync_time': last_sync_time.isoformat() if last_sync_time else None,
            'total_emails': total_emails,
            'processed_emails': processed_emails,
            'unprocessed_emails': unprocessed_emails,
            'recent_emails_7_days': recent_emails,
            'processing_rate': f"{processed_emails}/{total_emails}" if total_emails > 0 else "0/0"
        })
        
    except GmailToken.DoesNotExist:
        return Response({
            'error': '未找到Gmail认证信息',
            'sync_status': '未授权',
            'total_emails': 0,
            'processed_emails': 0,
            'unprocessed_emails': 0,
            'recent_emails_7_days': 0,
            'processing_rate': '0/0'
        }, status=400) 

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_gmail_auth_status(request):
    """检查用户的Gmail授权状态"""
    user = request.user
    
    try:
        gmail_token = GmailToken.objects.get(user=user)
        
        # 检查token是否过期
        is_expired = gmail_token.expires_at and gmail_token.expires_at < timezone.now()
        
        return Response({
            'is_authorized': True,
            'has_valid_token': not is_expired,
            'last_sync_time': gmail_token.last_sync_time.isoformat() if gmail_token.last_sync_time else None,
            'access_token_exists': bool(gmail_token.access_token),
            'token_expires_at': gmail_token.expires_at.isoformat() if gmail_token.expires_at else None,
            'user_id': user.id,
            'username': user.username
        })
        
    except GmailToken.DoesNotExist:
        return Response({
            'is_authorized': False,
            'has_valid_token': False,
            'last_sync_time': None,
            'access_token_exists': False,
            'token_expires_at': None,
            'user_id': user.id,
            'username': user.username
        }) 