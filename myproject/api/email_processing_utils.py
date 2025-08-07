"""
邮件处理工具模块
"""

import json
import logging
from datetime import datetime, timedelta
from django.utils import timezone
from datetime import timezone as dt_timezone
from .models import Category, Subcategory, Transaction, Email, GmailToken
from .gpt_service import parse_single_email
import requests

logger = logging.getLogger(__name__)

def build_gmail_query(last_sync_time):
    """
    构建Gmail查询参数，用于增量同步
    
    Args:
        last_sync_time: 上次同步时间
        
    Returns:
        str: Gmail查询字符串，如果无上次同步时间则返回None
    """
    if not last_sync_time:
        return None
    
    # 转换为Gmail支持的日期格式 YYYY/MM/DD
    date_str = last_sync_time.strftime('%Y/%m/%d')
    return f'after:{date_str}'

def get_incremental_sync_params(user, max_results=50):
    """
    获取增量同步的API参数
    
    Args:
        user: 用户对象
        max_results: 最大结果数量
        
    Returns:
        dict: API参数字典
    """
    try:
        gmail_token = GmailToken.objects.get(user=user)
        last_sync_time = gmail_token.last_sync_time
        
        params = {'maxResults': max_results}
        
        # 如果有上次同步时间，添加时间过滤
        if last_sync_time:
            query = build_gmail_query(last_sync_time)
            if query:
                params['q'] = query
                logger.info(f"使用增量同步，过滤时间: {last_sync_time}")
        else:
            logger.info("首次同步，获取最近7天的邮件")
            # 首次同步，获取最近7天的邮件
            seven_days_ago = timezone.now() - timedelta(days=7)
            date_str = seven_days_ago.strftime('%Y/%m/%d')
            params['q'] = f'after:{date_str}'
        
        return params
    except GmailToken.DoesNotExist:
        logger.error(f"用户 {user.username} 没有Gmail令牌")
        return {'maxResults': max_results}

def update_sync_time(user):
    """
    更新用户的同步时间
    
    Args:
        user: 用户对象
    """
    try:
        gmail_token = GmailToken.objects.get(user=user)
        gmail_token.last_sync_time = timezone.now()
        gmail_token.save()
        logger.info(f"更新用户 {user.username} 的同步时间为: {gmail_token.last_sync_time}")
    except GmailToken.DoesNotExist:
        logger.error(f"用户 {user.username} 没有Gmail令牌")

def create_transaction_from_gpt_result(transaction_data, email, user, dry_run=False):
    """从GPT解析结果创建交易记录"""
    try:
        if dry_run:
            return {
                'amount': str(transaction_data.get('amount', 0)),
                'currency': transaction_data.get('currency', 'USD'),
                'vendor': transaction_data.get('vendor', 'Unknown'),
                'category': transaction_data.get('category', 'Other'),
                'subcategory': transaction_data.get('subcategory', 'User defined'),
                'transaction_date': transaction_data.get('transaction_date', email.received_at.isoformat()),
                'item_name': transaction_data.get('item_name', 'Unknown Item'),
                'item_brand': transaction_data.get('item_brand', ''),
                'item_quantity': transaction_data.get('item_quantity', 1),
                'item_unit_price': transaction_data.get('item_unit_price', 0),
                'item_description': transaction_data.get('item_description', ''),
                'note': transaction_data.get('note', '')
            }
        
        # 获取或创建分类
        category_name = transaction_data.get('category', 'Other')
        category, _ = Category.objects.get_or_create(name=category_name)
        
        # 获取或创建子分类
        subcategory_name = transaction_data.get('subcategory', 'User defined')
        subcategory, _ = Subcategory.objects.get_or_create(
            category=category,
            name=subcategory_name,
            defaults={'color': '#808080'}
        )
        
        # 解析交易日期
        transaction_date_str = transaction_data.get('transaction_date')
        if transaction_date_str:
            try:
                transaction_date = timezone.datetime.strptime(
                    transaction_date_str, '%Y-%m-%d'
                ).replace(tzinfo=dt_timezone.utc)
            except ValueError:
                transaction_date = email.received_at
        else:
            transaction_date = email.received_at
        
        # 创建交易记录
        transaction = Transaction.objects.create(
            user=user,
            email=email,
            category=category,
            subcategory=subcategory,
            item_name=transaction_data.get('item_name', 'Unknown Item'),
            item_brand=transaction_data.get('item_brand', ''),
            item_quantity=transaction_data.get('item_quantity', 1),
            item_unit_price=transaction_data.get('item_unit_price', 0),
            item_description=transaction_data.get('item_description', ''),
            amount=transaction_data.get('amount', 0),
            currency=transaction_data.get('currency', 'USD'),
            vendor=transaction_data.get('vendor', 'Unknown'),
            transaction_date=transaction_date,
            note=transaction_data.get('note', '')
        )
        
        return {
            'id': transaction.id,
            'amount': str(transaction.amount),
            'currency': transaction.currency,
            'vendor': transaction.vendor,
            'category': category.name,
            'subcategory': subcategory.name,
            'transaction_date': transaction.transaction_date.isoformat(),
            'item_name': transaction.item_name,
            'item_brand': transaction.item_brand,
            'item_quantity': transaction.item_quantity,
            'item_unit_price': str(transaction.item_unit_price),
            'item_description': transaction.item_description,
            'note': transaction.note
        }
        
    except Exception as e:
        logger.error(f"创建交易记录失败 (邮件ID: {email.id}): {e}")
        return None

def process_emails_batch(emails, user, dry_run=False):
    """批量处理邮件"""
    results = {
        'processed_count': 0,
        'transactions_created': 0,
        'success_emails': [],
        'failed_emails': [],
        'total_emails': len(emails)
    }
    
    for email in emails:
        try:
            # 调用GPT解析
            parse_result = parse_single_email(email)
            
            if parse_result.get('has_transaction') and parse_result.get('transactions'):
                email_transactions = []
                transactions_created = 0
                
                for transaction_data in parse_result['transactions']:
                    transaction_info = create_transaction_from_gpt_result(
                        transaction_data, email, user, dry_run
                    )
                    
                    if transaction_info:
                        email_transactions.append(transaction_info)
                        transactions_created += 1
                
                # 标记邮件为已处理
                if not dry_run:
                    email.is_processed = True
                    email.processed_at = timezone.now()
                    email.save()
                
                results['success_emails'].append({
                    'id': email.id,
                    'subject': email.subject,
                    'transactions_count': transactions_created,
                    'transactions': email_transactions
                })
                results['transactions_created'] += transactions_created
                results['processed_count'] += 1
            else:
                # 没有识别到交易，也标记为已处理
                if not dry_run:
                    email.is_processed = True
                    email.processed_at = timezone.now()
                    email.save()
                
                results['success_emails'].append({
                    'id': email.id,
                    'subject': email.subject,
                    'transactions_count': 0,
                    'message': '未识别到交易信息'
                })
                results['processed_count'] += 1
                
        except Exception as e:
            logger.error(f"处理邮件失败 (邮件ID: {email.id}): {e}")
            results['failed_emails'].append({
                'id': email.id,
                'subject': email.subject,
                'error': str(e)
            })
    
    # 添加统计信息
    results['success_rate'] = f"{results['processed_count']}/{results['total_emails']}"
    
    return results 