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
import html as html_lib
from django.utils import timezone
from datetime import timedelta
from .models import GmailToken, Email

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def gmail_auth_url(request):
    """Generate Gmail OAuth authorization URL"""
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
    """Gmail OAuth callback"""
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
    
    # Save token to database
    GmailToken.objects.update_or_create(
        user=user,
        defaults={
            'access_token': access_token,
            'refresh_token': token_info.get('refresh_token'),
            'expires_at': timezone.now() + timedelta(seconds=token_info.get('expires_in', 3600))
        }
    )
    
    frontend_base = getattr(settings, 'FRONTEND_BASE_URL', 'http://localhost:3000')
    redirect_url = f"{frontend_base.rstrip('/')}/gmail-success?access_token={access_token}"
    return redirect(redirect_url)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sync_emails(request):
    """Sync emails to database (supports incremental sync)"""
    user = request.user
    auto_process = request.GET.get('auto_process', 'true').lower() == 'true'
    max_results = int(request.GET.get('max_results', 50))
    
    try:
        gmail_token = GmailToken.objects.get(user=user)
    except GmailToken.DoesNotExist:
        return Response({'error': 'No Gmail token found for this user'}, status=400)
    
    # Use incremental sync params
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
        # Fetch message detail
        msg_detail = requests.get(
            f"{gmail_api}/{msg['id']}",
            headers=headers
        ).json()
        
        # Parse headers
        headers_dict = {h['name']: h['value'] for h in msg_detail.get('payload', {}).get('headers', [])}
        
        # Parse received time
        try:
            received_at = parsedate_to_datetime(headers_dict.get('Date', ''))
        except:
            received_at = timezone.now()
        
    # Parse email body (improved: recursively parse; prefer text/plain, fallback to text/html preserving structure)
    def decode_part_data(data_str):
        if not data_str:
            return ''
        try:
            return base64.urlsafe_b64decode(data_str + '=' * (4 - len(data_str) % 4)).decode('utf-8', errors='ignore')
        except Exception:
            return ''

    def html_to_text_preserve_newlines(html_content: str) -> str:
        if not html_content:
            return ''
        # Replace common block tags with newlines, remove other tags, unescape entities
        import re
        text = html_content
        text = re.sub(r'(?i)</?(br|p|div|li|tr|td|th|h[1-6])[^>]*>', '\n', text)
        text = re.sub(r'<[^>]+>', '', text)
        text = html_lib.unescape(text)
        # Normalize line breaks while preserving structure
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        text = re.sub(r'[ \t\u00A0]{2,}', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        # Trim each line
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join([l for l in lines if l])
        return text.strip()

    def extract_payload_text(payload_obj):
        plain_texts = []
        html_texts = []

        if not payload_obj:
            return ''

        mime_type = payload_obj.get('mimeType')
        body_data = payload_obj.get('body', {}).get('data', '')

        if mime_type == 'text/plain':
            decoded = decode_part_data(body_data)
            if decoded:
                plain_texts.append(decoded)
        elif mime_type == 'text/html':
            decoded_html = decode_part_data(body_data)
            if decoded_html:
                html_texts.append(html_to_text_preserve_newlines(decoded_html))
        elif mime_type and mime_type.startswith('multipart/'):
            for sub in payload_obj.get('parts', []):
                sub_text = extract_payload_text(sub)
                if sub_text:
                    # Sub-result already prioritized; append directly
                    plain_texts.append(sub_text)
        else:
            # Top-level may carry body directly
            if body_data:
                decoded = decode_part_data(body_data)
                if decoded:
                    plain_texts.append(decoded)

        # Prefer plain over html; if both exist, concatenate with newlines
        if plain_texts:
            return '\n\n'.join([t for t in plain_texts if t])
        if html_texts:
            return '\n\n'.join([t for t in html_texts if t])
        return ''

        payload = msg_detail.get('payload', {})
        body_text = extract_payload_text(payload)
        
        # Save to DB with sync timestamp
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
                'last_sync_time': timezone.now()  # record sync time
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
    
    # Update global sync time
    update_sync_time(user)
    
    # Auto process emails
    auto_process_result = None
    if auto_process and newly_created_emails:
        try:
            from .email_processing_utils import process_emails_batch
            auto_process_result = process_emails_batch(newly_created_emails, user)
        except Exception as e:
            print(f"Auto-processing emails failed: {e}")
    
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
    """List user's emails"""
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
    """Get detail of a single email"""
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
    """Keep API compatibility with previous endpoint"""
    return sync_emails(request) 

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_sync_stats(request):
    """Get sync statistics"""
    user = request.user
    
    try:
        gmail_token = GmailToken.objects.get(user=user)
        
        # Stats
        total_emails = Email.objects.filter(user=user).count()
        processed_emails = Email.objects.filter(user=user, is_processed=True).count()
        unprocessed_emails = Email.objects.filter(user=user, is_processed=False).count()
        
        # Last sync
        last_sync_time = gmail_token.last_sync_time
        sync_status = "Synced" if last_sync_time else "Not synced"
        
        # Recent 7 days
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
            'error': 'No Gmail authorization found',
            'sync_status': 'Unauthorized',
            'total_emails': 0,
            'processed_emails': 0,
            'unprocessed_emails': 0,
            'recent_emails_7_days': 0,
            'processing_rate': '0/0'
        }, status=400) 

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_gmail_auth_status(request):
    """Check Gmail authorization status for current user"""
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