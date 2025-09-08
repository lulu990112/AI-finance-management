"""
email_processing_utils.py

This module contains utilities for parsing emails and converting GPT results
into `Transaction` records, plus helpers for incremental Gmail sync and
updating sync timestamps.

Main methods:
- build_gmail_query(last_sync_time)
- get_incremental_sync_params(user, max_results=50)
- update_sync_time
- create_transaction_from_gpt_result
- process_emails_batch(emails, user)
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
    Build Gmail query string for incremental sync
    
    Args:
        last_sync_time: last sync datetime
        
    Returns:
        str: Gmail query string, or None if no last sync time
    """
    if not last_sync_time:
        return None
    
    # Convert to Gmail-supported date format YYYY/MM/DD
    date_str = last_sync_time.strftime('%Y/%m/%d')
    return f'after:{date_str}'

def get_incremental_sync_params(user, max_results=50):
    """
    Get API params for incremental sync
    
    Args:
        user: user object
        max_results: max results
        
    Returns:
        dict: params dict
    """
    try:
        gmail_token = GmailToken.objects.get(user=user)
        last_sync_time = gmail_token.last_sync_time
        
        params = {'maxResults': max_results}
        
        # If we have last sync time, add time filter
        if last_sync_time:
            query = build_gmail_query(last_sync_time)
            if query:
                params['q'] = query
                logger.info(f"Using incremental sync, filter after: {last_sync_time}")
        else:
            logger.info("First-time sync, fetching emails from last 30 days")
            # First sync: last 30 days
            seven_days_ago = timezone.now() - timedelta(days=30)
            date_str = seven_days_ago.strftime('%Y/%m/%d')
            params['q'] = f'after:{date_str}'
        
        return params
    except GmailToken.DoesNotExist:
        logger.error(f"User {user.username} has no Gmail token")
        return {'maxResults': max_results}

def update_sync_time(user):
    """
    Update user's last sync time
    
    Args:
        user: user object
    """
    try:
        gmail_token = GmailToken.objects.get(user=user)
        gmail_token.last_sync_time = timezone.now()
        gmail_token.save()
        logger.info(f"Updated user {user.username} last sync time to: {gmail_token.last_sync_time}")
    except GmailToken.DoesNotExist:
        logger.error(f"User {user.username} has no Gmail token")

def create_transaction_from_gpt_result(transaction_data, email, user):
    """Create a Transaction from GPT parsed result"""
    try:
        # Get or create category
        category_name = transaction_data.get('category', 'Other')
        category, _ = Category.objects.get_or_create(name=category_name)
        
        # Get or create subcategory
        subcategory_name = transaction_data.get('subcategory', 'User defined')
        subcategory, _ = Subcategory.objects.get_or_create(
            category=category,
            name=subcategory_name,
            defaults={'color': '#808080'}
        )
        
        # Prefer email received time as transaction date
        transaction_date = email.received_at
        
        # Create transaction
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
        logger.error(f"Failed to create transaction (email ID: {email.id}): {e}")
        return None

def process_emails_batch(emails, user):
    """Process emails in batch"""
    results = {
        'processed_count': 0,
        'transactions_created': 0,
        'success_emails': [],
        'failed_emails': [],
        'total_emails': len(emails)
    }
    
    for email in emails:
        try:
            # Parse email via GPT
            parse_result = parse_single_email(email)
            
            if parse_result.get('has_transaction') and parse_result.get('transactions'):
                email_transactions = []
                transactions_created = 0
                
                for transaction_data in parse_result['transactions']:
                    transaction_info = create_transaction_from_gpt_result(
                        transaction_data, email, user
                    )
                    
                    if transaction_info:
                        email_transactions.append(transaction_info)
                        transactions_created += 1
                
                # Mark email as processed
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
                # No transactions detected; still mark as processed
                email.is_processed = True
                email.processed_at = timezone.now()
                email.save()
                
                results['success_emails'].append({
                    'id': email.id,
                    'subject': email.subject,
                    'transactions_count': 0,
                    'message': 'No transactions identified'
                })
                results['processed_count'] += 1
                
        except Exception as e:
            logger.error(f"Failed to process email (email ID: {email.id}): {e}")
            results['failed_emails'].append({
                'id': email.id,
                'subject': email.subject,
                'error': str(e)
            })
    
    # Add stats summary
    results['success_rate'] = f"{results['processed_count']}/{results['total_emails']}"
    
    return results 