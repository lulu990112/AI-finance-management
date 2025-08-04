from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import timezone as dt_timezone
from .models import Email, Category, Subcategory, Transaction, GmailToken
from .gpt_service import parse_single_email
from .email_processing_utils import process_emails_batch
import logging
import json
import requests
from email.utils import parsedate_to_datetime

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_unprocessed_emails(request):
    """获取未处理的邮件列表"""
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 10))
    
    emails = Email.objects.filter(
        user=request.user,
        is_processed=False
    ).order_by('-received_at')
    
    start = (page - 1) * page_size
    end = start + page_size
    
    email_list = []
    for email in emails[start:end]:
        email_list.append({
            'id': email.id,
            'subject': email.subject,
            'sender': email.sender,
            'snippet': email.snippet,
            'received_at': email.received_at.isoformat(),
            'has_body': bool(email.body)
        })
    
    return Response({
        'emails': email_list,
        'total': emails.count(),
        'page': page,
        'page_size': page_size
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_categories(request):
    """获取所有分类和子分类"""
    categories = Category.objects.prefetch_related('subcategories').all()
    
    category_list = []
    for category in categories:
        subcategories = []
        for subcategory in category.subcategories.all():
            subcategories.append({
                'id': subcategory.id,
                'name': subcategory.name,
                'color': subcategory.color
            })
        
        category_list.append({
            'id': category.id,
            'name': category.name,
            'subcategories': subcategories
        })
    
    return Response({'categories': category_list})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_transactions(request):
    """获取用户的交易记录"""
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 20))
    
    transactions = Transaction.objects.filter(user=request.user).select_related(
        'subcategory', 'email'
    ).order_by('-transaction_date')
    
    start = (page - 1) * page_size
    end = start + page_size
    
    transaction_list = []
    for transaction in transactions[start:end]:
        transaction_list.append({
            'id': transaction.id,
            'amount': str(transaction.amount),
            'currency': transaction.currency,
            'vendor': transaction.vendor,
            'category': transaction.category.name,
            'subcategory': transaction.subcategory.name,
            'transaction_date': transaction.transaction_date.isoformat(),
            'source': transaction.source,
            'note': transaction.note,
            'item_name': transaction.item_name,
            'item_brand': transaction.item_brand,
            'item_quantity': transaction.item_quantity,
            'item_unit_price': str(transaction.item_unit_price),
            'email_subject': transaction.email.subject if transaction.email else None
        })
    
    return Response({
        'transactions': transaction_list,
        'total': transactions.count(),
        'page': page,
        'page_size': page_size
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_processing_stats(request):
    """获取邮件处理统计信息"""
    user = request.user
    
    total_emails = Email.objects.filter(user=user).count()
    processed_emails = Email.objects.filter(user=user, is_processed=True).count()
    unprocessed_emails = Email.objects.filter(user=user, is_processed=False).count()
    total_transactions = Transaction.objects.filter(user=user).count()
    
    # 按分类统计交易
    category_stats = {}
    transactions = Transaction.objects.filter(user=user).select_related('category')
    
    for transaction in transactions:
        category_name = transaction.category.name
        if category_name not in category_stats:
            category_stats[category_name] = {
                'count': 0,
                'total_amount': 0
            }
        category_stats[category_name]['count'] += 1
        category_stats[category_name]['total_amount'] += float(transaction.amount)
    
    return Response({
        'total_emails': total_emails,
        'processed_emails': processed_emails,
        'unprocessed_emails': unprocessed_emails,
        'total_transactions': total_transactions,
        'processing_rate': f"{processed_emails}/{total_emails}" if total_emails > 0 else "0/0",
        'category_stats': category_stats
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def batch_sync_and_process_emails(request):
    """批量拉取邮件并自动处理"""
    user = request.user
    
    # 获取请求参数
    max_sync_emails = request.data.get('max_sync_emails', 50)
    max_process_emails = request.data.get('max_process_emails', 20)
    auto_process = request.data.get('auto_process', True)
    
    try:
        # 检查用户是否有Gmail token
        try:
            gmail_token = GmailToken.objects.get(user=user)
        except GmailToken.DoesNotExist:
            return Response({
                'error': '未找到Gmail认证信息，请先完成Gmail授权',
                'sync_count': 0,
                'processed_count': 0,
                'transactions_created': 0
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 从Gmail API拉取邮件
        headers = {'Authorization': f'Bearer {gmail_token.access_token}'}
        gmail_api = 'https://gmail.googleapis.com/gmail/v1/users/me/messages'
        params = {'maxResults': max_sync_emails}
        
        r = requests.get(gmail_api, headers=headers, params=params)
        if r.status_code != 200:
            return Response({
                'error': 'Gmail API请求失败',
                'details': r.json(),
                'sync_count': 0,
                'processed_count': 0,
                'transactions_created': 0
            }, status=status.HTTP_400_BAD_REQUEST)
        
        messages = r.json().get('messages', [])
        if not messages:
            return Response({
                'message': 'Gmail中没有找到邮件',
                'sync_count': 0,
                'processed_count': 0,
                'transactions_created': 0
            })
        
        # 保存邮件到数据库
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
                                import base64
                                body_text = base64.urlsafe_b64decode(body_data + '=' * (4 - len(body_data) % 4)).decode('utf-8')
                                break
                            except:
                                pass
            else:
                body_data = payload.get('body', {}).get('data', '')
                if body_data:
                    try:
                        import base64
                        body_text = base64.urlsafe_b64decode(body_data + '=' * (4 - len(body_data) % 4)).decode('utf-8')
                    except:
                        pass
            
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
                    'body': body_text,
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
                'created': created
            })
            
            if created:
                newly_created_emails.append(email_obj)
        
        # 自动处理邮件
        process_results = None
        if auto_process and newly_created_emails:
            try:
                emails_to_process = newly_created_emails[:max_process_emails]
                process_results = process_emails_batch(emails_to_process, user)
            except Exception as e:
                logger.error(f"自动处理邮件失败: {e}")
                process_results = {
                    'error': f'自动处理失败: {e}',
                    'processed_count': 0,
                    'transactions_created': 0
                }
        
        # 构建响应数据
        response_data = {
            'message': f'成功同步 {len(saved_emails)} 封邮件',
            'sync_stats': {
                'total_synced': len(saved_emails),
                'newly_created': len(newly_created_emails),
                'already_existed': len(saved_emails) - len(newly_created_emails)
            },
            'emails': saved_emails,
            'auto_process_enabled': auto_process
        }
        
        if process_results:
            response_data['process_results'] = process_results
        
        return Response(response_data)
        
    except Exception as e:
        logger.error(f"批量同步和处理邮件失败: {e}")
        return Response({
            'error': f'批量操作失败: {e}',
            'sync_count': 0,
            'processed_count': 0,
            'transactions_created': 0
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 