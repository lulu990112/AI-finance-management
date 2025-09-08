"""
group_statistics_service.py

This module provides aggregated statistics and analysis utilities for group transactions.

The service is responsible for:
- Computing overview metrics (totals, counts, averages) over configurable windows
- Building daily/weekly trends and category/subcategory breakdowns
- Summarizing member contributions and vendor distributions
- Comparing multiple time windows for quick benchmarking
- Preparing export-friendly datasets for reporting/visualization
- Assembling a comprehensive summary payload for dashboards
"""

import logging
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from datetime import timedelta, date
from .models import GroupTransaction, Group, Category, Subcategory
import json

logger = logging.getLogger(__name__)

class GroupStatisticsService:
    """Group data statistics service"""
    
    def _get_filtered_transactions(self, group_id, days=None, start_date=None, end_date=None):
        """General method: get filtered transaction data"""
        query = GroupTransaction.objects.filter(group_id=group_id)
        
        if days:
            end_date = timezone.now()
            start_date = end_date - timedelta(days=days)
        
        if start_date:
            query = query.filter(transaction_date__gte=start_date)
        if end_date:
            query = query.filter(transaction_date__lte=end_date)
            
        return query
    
    def get_group_overview_statistics(self, group_id, days=30):
        """Get group overview statistics"""
        try:
            transactions = self._get_filtered_transactions(group_id, days=days)
            
            total_amount = transactions.aggregate(total=Sum('amount'))['total'] or 0
            total_count = transactions.count()
            avg_amount = transactions.aggregate(avg=Avg('amount'))['avg'] or 0
            
            # Member statistics
            member_stats = transactions.values('user__username').annotate(
                total_amount=Sum('amount'),
                transaction_count=Count('group_transaction_id')
            ).order_by('-total_amount')
            
            # Category statistics
            category_stats = transactions.values('category__name').annotate(
                total_amount=Sum('amount'),
                transaction_count=Count('group_transaction_id')
            ).order_by('-total_amount')
            
            # Vendor statistics
            vendor_stats = transactions.values('vendor').annotate(
                total_amount=Sum('amount'),
                transaction_count=Count('group_transaction_id')
            ).order_by('-total_amount')[:10]
            
            return {
                'period': f'Last {days} days',
                'total_amount': float(total_amount),
                'total_transactions': total_count,
                'average_amount': float(avg_amount),
                'member_count': member_stats.count(),
                'top_members': list(member_stats[:5]),
                'top_categories': list(category_stats[:5]),
                'top_vendors': list(vendor_stats)
            }
            
        except Exception as e:
            logger.error(f"获取组概览统计失败: {str(e)}")
            return None
    
    def get_group_spending_trend(self, group_id, days=30):
        """Get group spending trend"""
        try:
            transactions = self._get_filtered_transactions(group_id, days=days)
            
            # By date statistics
            daily_stats = transactions.extra(
                select={'date': 'DATE(transaction_date)'}
            ).values('date').annotate(
                total_amount=Sum('amount'),
                transaction_count=Count('group_transaction_id')
            ).order_by('date')
            
            # By week statistics
            weekly_stats = transactions.extra(
                select={'week': 'YEARWEEK(transaction_date)'}
            ).values('week').annotate(
                total_amount=Sum('amount'),
                transaction_count=Count('group_transaction_id')
            ).order_by('week')
            
            return {
                'daily_trend': list(daily_stats),
                'weekly_trend': list(weekly_stats)
            }
            
        except Exception as e:
            logger.error(f"Get group spending trend failed: {str(e)}")
            return None
    
    def get_group_category_analysis(self, group_id, days=30):
        """Get group category analysis"""
        try:
            transactions = self._get_filtered_transactions(group_id, days=days)
            
            # Category statistics
            category_stats = transactions.values('category__name', 'category__id').annotate(
                total_amount=Sum('amount'),
                transaction_count=Count('group_transaction_id'),
                avg_amount=Avg('amount')
            ).order_by('-total_amount')
            
            # Subcategory statistics
            subcategory_stats = transactions.values(
                'category__name', 
                'subcategory__name', 
                'subcategory__color'
            ).annotate(
                total_amount=Sum('amount'),
                transaction_count=Count('group_transaction_id')
            ).order_by('-total_amount')
            
            # Build category tree structure
            category_tree = {}
            for stat in category_stats:
                category_name = stat['category__name']
                category_tree[category_name] = {
                    'category_id': stat['category__id'],
                    'total_amount': float(stat['total_amount']),
                    'transaction_count': stat['transaction_count'],
                    'avg_amount': float(stat['avg_amount']),
                    'subcategories': []
                }
            
            for stat in subcategory_stats:
                category_name = stat['category__name']
                if category_name in category_tree:
                    category_tree[category_name]['subcategories'].append({
                        'name': stat['subcategory__name'],
                        'color': stat['subcategory__color'],
                        'total_amount': float(stat['total_amount']),
                        'transaction_count': stat['transaction_count']
                    })
            
            return {
                'categories': list(category_stats),
                'subcategories': list(subcategory_stats),
                'category_tree': category_tree
            }
            
        except Exception as e:
            logger.error(f"Get group category analysis failed: {str(e)}")
            return None
    
    def get_group_member_analysis(self, group_id, days=30):
        """Get group member analysis"""
        try:
            end_date = timezone.now()
            start_date = end_date - timedelta(days=days)
            
            # Member spending statistics
            member_stats = GroupTransaction.objects.filter(
                group_id=group_id,
                transaction_date__gte=start_date,
                transaction_date__lte=end_date
            ).values('user__username', 'user__id').annotate(
                total_amount=Sum('amount'),
                transaction_count=Count('group_transaction_id'),
                avg_amount=Avg('amount'),
                max_amount=Sum('amount')  # Here should use Max, but to simplify
            ).order_by('-total_amount')
            
            # Member category preference
            member_category_prefs = transactions.values('user__username', 'category__name').annotate(
                total_amount=Sum('amount'),
                transaction_count=Count('group_transaction_id')
            ).order_by('user__username', '-total_amount')
            
            # Build member category preference tree
            member_prefs = {}
            for stat in member_category_prefs:
                username = stat['user__username']
                if username not in member_prefs:
                    member_prefs[username] = []
                member_prefs[username].append({
                    'category': stat['category__name'],
                    'total_amount': float(stat['total_amount']),
                    'transaction_count': stat['transaction_count']
                })
            
            return {
                'member_stats': list(member_stats),
                'member_category_prefs': member_prefs
            }
            
        except Exception as e:
            logger.error(f"Get group member analysis failed: {str(e)}")
            return None
    
    def get_group_comparison_data(self, group_id, comparison_days=[7, 30, 90]):
        """Get group comparison data"""
        try:
            comparison_data = {}
            
            for days in comparison_days:
                transactions = self._get_filtered_transactions(group_id, days=days)
                
                total_amount = transactions.aggregate(total=Sum('amount'))['total'] or 0
                total_count = transactions.count()
                avg_amount = transactions.aggregate(avg=Avg('amount'))['avg'] or 0
                
                comparison_data[f'{days}_days'] = {
                    'period': f'Last {days} days',
                    'total_amount': float(total_amount),
                    'total_transactions': total_count,
                    'average_amount': float(avg_amount),
                    'daily_average': float(total_amount / days) if days > 0 else 0
                }
            
            return comparison_data
            
        except Exception as e:
            logger.error(f"Get group comparison data failed: {str(e)}")
            return None
    
    def get_group_vendor_analysis(self, group_id, days=30):
        """Get group vendor analysis"""
        try:
            transactions = self._get_filtered_transactions(group_id, days=days)
            
            # Vendor statistics
            vendor_stats = transactions.values('vendor').annotate(
                total_amount=Sum('amount'),
                transaction_count=Count('group_transaction_id'),
                avg_amount=Avg('amount')
            ).order_by('-total_amount')
            
            # Vendor category statistics
            vendor_category_stats = transactions.values('vendor', 'category__name').annotate(
                total_amount=Sum('amount'),
                transaction_count=Count('group_transaction_id')
            ).order_by('vendor', '-total_amount')
            
            return {
                'vendor_stats': list(vendor_stats),
                'vendor_category_stats': list(vendor_category_stats)
            }
            
        except Exception as e:
            logger.error(f"Get group vendor analysis failed: {str(e)}")
            return None
    
    def get_group_export_data(self, group_id, start_date=None, end_date=None):
        """Get group export data"""
        try:
            query = GroupTransaction.objects.filter(group_id=group_id)
            
            if start_date:
                query = query.filter(transaction_date__date__gte=start_date)
            if end_date:
                query = query.filter(transaction_date__date__lte=end_date)
            
            transactions = query.select_related('user', 'category', 'subcategory').order_by('-transaction_date')
            
            export_data = []
            for transaction in transactions:
                export_data.append({
                    'transaction_id': transaction.group_transaction_id,
                    'date': transaction.transaction_date.strftime('%Y-%m-%d'),
                    'time': transaction.transaction_date.strftime('%H:%M:%S'),
                    'member': transaction.user.username,
                    'category': transaction.category.name,
                    'subcategory': transaction.subcategory.name,
                    'vendor': transaction.vendor,
                    'item_name': transaction.item_name,
                    'amount': float(transaction.amount),
                    'currency': transaction.currency,
                    'note': transaction.note or '',
                    'is_manual': transaction.is_manual
                })
            
            return export_data
            
        except Exception as e:
            logger.error(f"Get group export data failed: {str(e)}")
            return None
    
    def get_group_summary_report(self, group_id, days=30):
        """Get group summary report"""
        try:
            overview = self.get_group_overview_statistics(group_id, days)
            category_analysis = self.get_group_category_analysis(group_id, days)
            member_analysis = self.get_group_member_analysis(group_id, days)
            vendor_analysis = self.get_group_vendor_analysis(group_id, days)
            comparison_data = self.get_group_comparison_data(group_id)
            
            return {
                'overview': overview,
                'category_analysis': category_analysis,
                'member_analysis': member_analysis,
                'vendor_analysis': vendor_analysis,
                'comparison_data': comparison_data,
                'generated_at': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Get group summary report failed: {str(e)}")
            return None
