from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction as db_transaction, models
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
import json
from functools import wraps

from .models import Group, GroupTransaction, GroupAIReport, Transaction, Category, Subcategory
from .serializers import (
    GroupSerializer, GroupCreateSerializer, GroupMemberSerializer, GroupJoinSerializer,
    TransactionShareSerializer, GroupTransactionSerializer, GroupAIReportSerializer,
    CategorySerializer, SubcategorySerializer
)
from .group_ai_report_service import GroupAIReportGenerator
from .group_statistics_service import GroupStatisticsService


def handle_group_exceptions(func):
    """Decorator: unified exception handling for group-related views"""
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        try:
            return func(request, *args, **kwargs)
        except Exception as e:
            return Response({
                'success': False,
                'message': f'{func.__name__} failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return wrapper


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_group(request):
    """Create a new group"""
    serializer = GroupCreateSerializer(data=request.data)
    if serializer.is_valid():
        try:
            with db_transaction.atomic():
                # Generate new group ID
                max_group_id = Group.objects.aggregate(models.Max('group_id'))['group_id__max'] or 0
                new_group_id = max_group_id + 1
                
                # Create group record (creator)
                group = Group.objects.create(
                    user=request.user,
                    group_id=new_group_id,
                    group_name=serializer.validated_data['group_name'],
                    description=serializer.validated_data.get('description', ''),
                    max_members=serializer.validated_data.get('max_members', 10),
                    role='owner'
                )
                
                return Response({
                    'success': True,
                    'message': 'Group created successfully',
                    'group_id': new_group_id,
                    'group_name': group.group_name
                }, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Failed to create group: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response({
            'success': False,
            'message': 'Validation failed',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@handle_group_exceptions
def get_user_groups(request):
    """Get all groups of current user"""
    user_groups = Group.objects.filter(user=request.user).order_by('-created_at')
    serializer = GroupSerializer(user_groups, many=True)
    
    return Response({
        'success': True,
        'groups': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_group_info(request, group_id):
    """Get group detail"""
    try:
        # Check if current user is a member of this group
        user_membership = Group.objects.filter(user=request.user, group_id=group_id).first()
        if not user_membership:
            return Response({
                'success': False,
                'message': 'You are not a member of this group'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get group info
        group_info = Group.get_group_info(group_id)
        if not group_info:
            return Response({
                'success': False,
                'message': 'Group not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get group members
        members = Group.get_group_members(group_id)
        member_serializer = GroupMemberSerializer(members, many=True)
        
        return Response({
            'success': True,
            'group_info': group_info,
            'members': member_serializer.data,
            'user_role': user_membership.role
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to get group info: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def join_group(request):
    """Join group"""
    serializer = GroupJoinSerializer(data=request.data)
    if serializer.is_valid():
        group_id = serializer.validated_data['group_id']
        
        try:
            with db_transaction.atomic():
                # Check if group exists
                group_info = Group.get_group_info(group_id)
                if not group_info:
                    return Response({
                        'success': False,
                        'message': 'Group does not exist'
                    }, status=status.HTTP_404_NOT_FOUND)
                
                # Check if user is already a member
                existing_membership = Group.objects.filter(user=request.user, group_id=group_id).first()
                if existing_membership:
                    return Response({
                        'success': False,
                        'message': 'You are already a member of this group'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Check if group is full
                member_count = Group.objects.filter(group_id=group_id).count()
                if member_count >= group_info['max_members']:
                    return Response({
                        'success': False,
                        'message': 'Group is full'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Join group
                Group.objects.create(
                    user=request.user,
                    group_id=group_id,
                    role='member'
                )
                
                return Response({
                    'success': True,
                    'message': 'Joined group successfully',
                    'group_id': group_id,
                    'group_name': group_info['group_name']
                }, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Failed to join group: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response({
            'success': False,
            'message': 'Validation failed',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def leave_group(request, group_id):
    """Leave group"""
    try:
        with db_transaction.atomic():
            # Check membership
            membership = Group.objects.filter(user=request.user, group_id=group_id).first()
            if not membership:
                return Response({
                    'success': False,
                    'message': 'You are not a member of this group'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # If owner, need special handling
            if membership.role == 'owner':
                # If owner, ensure there are no other members first
                other_members = Group.objects.filter(group_id=group_id).exclude(user=request.user)
                if other_members.exists():
                    return Response({
                        'success': False,
                        'message': 'Owner cannot leave the group. Transfer ownership or disband the group first.'
                    }, status=status.HTTP_400_BAD_REQUEST)
                else:
                    # No other members: delete whole group
                    Group.objects.filter(group_id=group_id).delete()
                    GroupTransaction.objects.filter(group_id=group_id).delete()
                    GroupAIReport.objects.filter(group_id=group_id).delete()
                    
                    return Response({
                        'success': True,
                        'message': 'Group disbanded'
                    }, status=status.HTTP_200_OK)
            else:
                # Non-owner member leaves
                membership.delete()
                
                return Response({
                    'success': True,
                    'message': 'Left group successfully'
                }, status=status.HTTP_200_OK)
                
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to leave group: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def share_transactions(request):
    """Share transactions to group"""
    logger.debug(f"Start handling share transactions, user: {request.user.id}")
    logger.debug(f"Request data: {request.data}")
    
    serializer = TransactionShareSerializer(data=request.data)
    if serializer.is_valid():
        transaction_ids = serializer.validated_data['transaction_ids']
        group_ids = serializer.validated_data['group_ids']
        
        logger.debug(f"Validated. Transactions: {transaction_ids}, Groups: {group_ids}")
        
        try:
            with db_transaction.atomic():
                # Validate transactions belong to current user
                transactions = Transaction.objects.filter(
                    id__in=transaction_ids,
                    user=request.user
                )
                logger.debug(f"Found transactions: {len(transactions)}, expected: {len(transaction_ids)}")
                
                if len(transactions) != len(transaction_ids):
                    logger.warning(f"Transaction validation failed, user: {request.user.id}")
                    return Response({
                        'success': False,
                        'message': 'Some transactions do not exist or do not belong to you'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Validate user membership in all specified groups
                user_groups = Group.objects.filter(
                    user=request.user,
                    group_id__in=group_ids
                ).values_list('group_id', flat=True)
                
                logger.debug(f"User groups: {list(user_groups)}, requested: {group_ids}")
                
                if len(user_groups) != len(group_ids):
                    logger.warning(f"Group validation failed, user: {request.user.id}")
                    return Response({
                        'success': False,
                        'message': 'You are not a member of some specified groups'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Share transactions to groups
                shared_count = 0
                for transaction in transactions:
                    for group_id in group_ids:
                        logger.debug(f"Try sharing transaction {transaction.id} to group {group_id}")
                        if group_id not in transaction.shared_to_groups:
                            try:
                                transaction.share_to_group(group_id)
                                shared_count += 1
                                logger.debug(f"Shared transaction {transaction.id} to group {group_id}")
                            except Exception as e:
                                logger.error(f"Failed to share transaction {transaction.id} to group {group_id}: {str(e)}")
                                raise
                
                logger.info(f"Share completed, success count: {shared_count}")
                return Response({
                    'success': True,
                    'message': f'Shared {shared_count} transactions',
                    'shared_count': shared_count
                }, status=status.HTTP_200_OK)
                
        except Exception as e:
            import traceback
            logger.error(f"Share transactions failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return Response({
                'success': False,
                'message': f'Failed to share transactions: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response({
            'success': False,
            'message': 'Validation failed',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_group_transactions(request, group_id):
    """Get group transactions"""
    try:
        # Check membership
        membership = Group.objects.filter(user=request.user, group_id=group_id).first()
        if not membership:
            return Response({
                'success': False,
                'message': 'You are not a member of this group'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Query params
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        category_id = request.GET.get('category_id')
        
        # Query group transactions
        transactions = GroupTransaction.objects.filter(group_id=group_id)
        
        # Apply filters
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                transactions = transactions.filter(transaction_date__date__gte=start_date)
            except ValueError:
                pass
        
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                transactions = transactions.filter(transaction_date__date__lte=end_date)
            except ValueError:
                pass
        
        if category_id:
            transactions = transactions.filter(category_id=category_id)
        
        # Serialize
        serializer = GroupTransactionSerializer(transactions, many=True)
        
        # Stats
        total_amount = sum(t.amount for t in transactions)
        total_count = transactions.count()
        
        return Response({
            'success': True,
            'transactions': serializer.data,
            'total_amount': float(total_amount),
            'total_count': total_count
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to get group transactions: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_manual_transaction(request, group_id):
    """Add manual group transaction"""
    try:
        # Check membership
        membership = Group.objects.filter(user=request.user, group_id=group_id).first()
        if not membership:
            return Response({
                'success': False,
                'message': 'You are not a member of this group'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Required fields
        required_fields = ['item_name', 'amount', 'vendor', 'transaction_date', 'category_id', 'subcategory_id']
        for field in required_fields:
            if field not in request.data:
                return Response({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with db_transaction.atomic():
                # Validate category & subcategory
                category = get_object_or_404(Category, id=request.data['category_id'])
                subcategory = get_object_or_404(Subcategory, id=request.data['subcategory_id'])
                
                # Create group transaction
                group_transaction = GroupTransaction.objects.create(
                    group_id=group_id,
                    user=request.user,
                    category=category,
                    subcategory=subcategory,
                    item_name=request.data['item_name'],
                    item_brand=request.data.get('item_brand', ''),
                    item_quantity=request.data.get('item_quantity', 1),
                    item_unit_price=request.data.get('item_unit_price', 0),
                    item_description=request.data.get('item_description', ''),
                    amount=request.data['amount'],
                    currency=request.data.get('currency', 'USD'),
                    vendor=request.data['vendor'],
                    transaction_date=datetime.strptime(request.data['transaction_date'], '%Y-%m-%d'),
                    source='manual',
                    note=request.data.get('note', ''),
                    is_manual=True
                )
                
                serializer = GroupTransactionSerializer(group_transaction)
                
                return Response({
                    'success': True,
                    'message': 'Manual transaction added successfully',
                    'transaction': serializer.data
                }, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Failed to add transaction: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to add transaction: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_group_ai_reports(request, group_id):
    """Get group AI reports"""
    try:
        # Check membership
        membership = Group.objects.filter(user=request.user, group_id=group_id).first()
        if not membership:
            return Response({
                'success': False,
                'message': 'You are not a member of this group'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get group AI reports
        reports = GroupAIReport.objects.filter(group_id=group_id).order_by('-report_date')
        serializer = GroupAIReportSerializer(reports, many=True)
        
        return Response({
            'success': True,
            'reports': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to get group AI reports: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_categories(request):
    """Get categories (for front-end selects)"""
    try:
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        
        return Response({
            'success': True,
            'categories': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to get categories: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_subcategories(request, category_id):
    """Get subcategories for a category"""
    try:
        subcategories = Subcategory.objects.filter(category_id=category_id)
        serializer = SubcategorySerializer(subcategories, many=True)
        
        return Response({
            'success': True,
            'subcategories': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to get subcategories: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_group_ai_report(request, group_id):
    """Generate group AI report"""
    try:
        # Check membership
        membership = Group.objects.filter(user=request.user, group_id=group_id).first()
        if not membership:
            return Response({
                'success': False,
                'message': 'You are not a member of this group'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Params
        analysis_period_days = request.data.get('analysis_period_days', 30)
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        
        # Initialize report generator
        generator = GroupAIReportGenerator()
        
        if start_date and end_date:
            # Generate report for specified period
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                report = generator.generate_group_biweekly_report(group_id, start_date, end_date)
            except ValueError:
                return Response({
                    'success': False,
                    'message': 'Invalid date format. Use YYYY-MM-DD.'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Generate report for recent N days
            report = generator.generate_group_report(group_id, analysis_period_days)
        
        serializer = GroupAIReportSerializer(report)
        
        return Response({
            'success': True,
            'message': 'Group AI report generated successfully',
            'report': serializer.data
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to generate group AI report: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_group_statistics(request, group_id):
    """Get group statistics"""
    try:
        # Check membership
        membership = Group.objects.filter(user=request.user, group_id=group_id).first()
        if not membership:
            return Response({
                'success': False,
                'message': 'You are not a member of this group'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Query params
        days = int(request.GET.get('days', 30))
        stat_type = request.GET.get('type', 'overview')  # overview, trend, category, member, vendor, summary
        
        # Initialize statistics service
        stats_service = GroupStatisticsService()
        
        if stat_type == 'overview':
            data = stats_service.get_group_overview_statistics(group_id, days)
        elif stat_type == 'trend':
            data = stats_service.get_group_spending_trend(group_id, days)
        elif stat_type == 'category':
            data = stats_service.get_group_category_analysis(group_id, days)
        elif stat_type == 'member':
            data = stats_service.get_group_member_analysis(group_id, days)
        elif stat_type == 'vendor':
            data = stats_service.get_group_vendor_analysis(group_id, days)
        elif stat_type == 'summary':
            data = stats_service.get_group_summary_report(group_id, days)
        else:
            return Response({
                'success': False,
                'message': 'Unsupported statistics type'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if data is None:
            return Response({
                'success': False,
                'message': 'Failed to get statistics data'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            'success': True,
            'data': data,
            'type': stat_type,
            'days': days
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to get group statistics: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_group_data(request, group_id):
    """Export group data"""
    try:
        # Check membership
        membership = Group.objects.filter(user=request.user, group_id=group_id).first()
        if not membership:
            return Response({
                'success': False,
                'message': 'You are not a member of this group'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get query parameters
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        # Parse dates
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            except ValueError:
                return Response({
                    'success': False,
                    'message': 'Invalid start_date format. Use YYYY-MM-DD.'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            except ValueError:
                return Response({
                    'success': False,
                    'message': 'Invalid end_date format. Use YYYY-MM-DD.'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get export data
        stats_service = GroupStatisticsService()
        export_data = stats_service.get_group_export_data(group_id, start_date, end_date)
        
        if export_data is None:
            return Response({
                'success': False,
                'message': 'Failed to export data'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            'success': True,
            'data': export_data,
            'total_count': len(export_data),
            'start_date': start_date.isoformat() if start_date else None,
            'end_date': end_date.isoformat() if end_date else None
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to export group data: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
