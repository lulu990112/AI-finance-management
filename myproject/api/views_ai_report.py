from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import AIReport
from .ai_report_service import AIReportGenerator
import logging

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_ai_report_detail(request, report_id):
    """获取单个AI报告详情"""
    try:
        report = AIReport.objects.get(
            id=report_id,
            user=request.user,
            is_generated=True
        )
        
        return Response({
            'message': 'AI report retrieved successfully',
            'report': report.get_report_data()
        })
        
    except AIReport.DoesNotExist:
        return Response({
            'error': 'AI report not found'
        }, status=status.HTTP_404_NOT_FOUND)
        
    except Exception as e:
        logger.error(f"获取AI报告详情失败: {str(e)}")
        return Response({
            'error': 'Failed to get AI report detail',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_ai_reports(request):
    """获取用户的AI报告列表"""
    try:
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))
        report_type = request.GET.get('report_type', 'all')  # all, general, biweekly, monthly
        
        # 构建查询条件
        query = AIReport.objects.filter(user=request.user, is_generated=True)
        
        if report_type != 'all':
            query = query.filter(report_type=report_type)
        
        reports = query.order_by('-report_date')
        
        start = (page - 1) * page_size
        end = start + page_size
        
        report_list = []
        for report in reports[start:end]:
            report_list.append(report.get_report_data())
        
        return Response({
            'reports': report_list,
            'total': reports.count(),
            'page': page,
            'page_size': page_size,
            'report_type': report_type
        })
        
    except Exception as e:
        logger.error(f"获取AI报告列表失败: {str(e)}")
        return Response({
            'error': 'Failed to get AI reports',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_latest_ai_report(request):
    """获取用户最新的AI报告"""
    try:
        report_type = request.GET.get('report_type', 'general')
        
        query = AIReport.objects.filter(
            user=request.user,
            is_generated=True,
            generation_status='completed'
        )
        
        if report_type != 'all':
            query = query.filter(report_type=report_type)
        
        report = query.order_by('-report_date').first()
        
        if not report:
            return Response({
                'message': 'No AI report found',
                'report': None
            })
        
        return Response({
            'message': 'Latest AI report retrieved successfully',
            'report': report.get_report_data()
        })
        
    except Exception as e:
        logger.error(f"获取最新AI报告失败: {str(e)}")
        return Response({
            'error': 'Failed to get latest AI report',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_biweekly_reports(request):
    """获取用户的半个月报告列表"""
    try:
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))
        
        reports = AIReport.objects.filter(
            user=request.user,
            report_type='biweekly',
            is_generated=True
        ).order_by('-report_period_start')
        
        start = (page - 1) * page_size
        end = start + page_size
        
        report_list = []
        for report in reports[start:end]:
            report_list.append(report.get_report_data())
        
        return Response({
            'reports': report_list,
            'total': reports.count(),
            'page': page,
            'page_size': page_size,
            'report_type': 'biweekly'
        })
        
    except Exception as e:
        logger.error(f"获取半个月报告列表失败: {str(e)}")
        return Response({
            'error': 'Failed to get biweekly reports',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_latest_biweekly_report(request):
    """获取用户最新的半个月报告"""
    try:
        report = AIReport.objects.filter(
            user=request.user,
            report_type='biweekly',
            is_generated=True,
            generation_status='completed'
        ).order_by('-report_period_start').first()
        
        if not report:
            return Response({
                'message': 'No biweekly report found',
                'report': None
            })
        
        return Response({
            'message': 'Latest biweekly report retrieved successfully',
            'report': report.get_report_data()
        })
        
    except Exception as e:
        logger.error(f"获取最新半个月报告失败: {str(e)}")
        return Response({
            'error': 'Failed to get latest biweekly report',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_biweekly_report_by_period(request, start_date, end_date):
    """获取指定周期的半个月报告"""
    try:
        from datetime import datetime
        
        # 解析日期参数
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return Response({
                'error': 'Invalid date format. Use YYYY-MM-DD format.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        report = AIReport.objects.filter(
            user=request.user,
            report_type='biweekly',
            report_period_start=start_date_obj,
            report_period_end=end_date_obj,
            is_generated=True
        ).first()
        
        if not report:
            return Response({
                'message': 'Biweekly report not found for the specified period',
                'report': None
            })
        
        return Response({
            'message': 'Biweekly report retrieved successfully',
            'report': report.get_report_data()
        })
        
    except Exception as e:
        logger.error(f"获取指定周期半个月报告失败: {str(e)}")
        return Response({
            'error': 'Failed to get biweekly report for the specified period',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_biweekly_report(request):
    """手动生成指定周期的半个月报告"""
    try:
        from datetime import datetime
        
        start_date_str = request.data.get('start_date')
        end_date_str = request.data.get('end_date')
        
        if not start_date_str or not end_date_str:
            return Response({
                'error': 'start_date and end_date are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({
                'error': 'Invalid date format. Use YYYY-MM-DD format.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查是否已有该周期的报告
        existing_report = AIReport.objects.filter(
            user=request.user,
            report_type='biweekly',
            report_period_start=start_date,
            report_period_end=end_date
        ).first()
        
        if existing_report:
            return Response({
                'message': 'Biweekly report already exists for this period',
                'report': existing_report.get_report_data(),
                'is_cached': True
            })
        
        # 生成新报告
        generator = AIReportGenerator()
        report = generator.generate_biweekly_report(request.user, start_date, end_date)
        
        return Response({
            'message': 'Biweekly report generated successfully',
            'report': report.get_report_data(),
            'is_cached': False
        })
        
    except Exception as e:
        logger.error(f"生成半个月报告失败: {str(e)}")
        return Response({
            'error': 'Failed to generate biweekly report',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

 