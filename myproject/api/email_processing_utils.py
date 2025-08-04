"""
邮件处理工具模块
"""

import logging
from django.utils import timezone
from datetime import timezone as dt_timezone
from .models import Category, Subcategory, Transaction
from .gpt_service import parse_single_email

logger = logging.getLogger(__name__)

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