"""
group_ai_report_service.py

This module generates AI financial reports for groups based on shared transactions, supporting both recent window analyses 
and specified biweekly periods.

The service is responsible for:
- Fetching group transactions with member/category context for a given period
- Reusing common analytics and prompt-building utilities for team-level insight
- Producing LLM-based content tailored to group spending behavior
- Persisting `GroupAIReport` records and avoiding duplicate period reports
- Handling empty datasets and error scenarios with structured fallbacks
"""

import logging
from django.utils import timezone
from datetime import timedelta, date
from .models import GroupTransaction, GroupAIReport
from .base_ai_report_service import BaseAIReportGenerator

logger = logging.getLogger(__name__)
# class Child(Parent) ！！！
class GroupAIReportGenerator(BaseAIReportGenerator):
    """Group AI financial report generator"""
    
    def generate_group_report(self, group_id, analysis_period_days=30):
        """Generate AI financial report for a group"""
        try:
            # Get group transactions
            end_date = timezone.now()
            start_date = end_date - timedelta(days=analysis_period_days)
            
            transactions = GroupTransaction.objects.filter(
                group_id=group_id,
                transaction_date__gte=start_date,
                transaction_date__lte=end_date
            ).select_related('category', 'subcategory', 'user')
            
            if not transactions.exists():
                return self._create_empty_report(group_id, analysis_period_days)
            
            # Analyze transactions ！！wrapper method call for generic method _analyze_transactions_base(...)
            analysis_data = self._analyze_group_transactions(transactions)
            
            # Generate report content! wrapper method call for generic method _generate_report_content_base(...)
            report_content = self._generate_report_content(analysis_data)
            
            # Save report ！！wrapper method call for generic method _save_report(...)
            report = self._save_report(group_id, report_content, analysis_data, analysis_period_days)
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate group AI report: {str(e)}")
            return self._create_error_report(group_id, analysis_period_days, str(e))
    
    def generate_group_biweekly_report(self, group_id, start_date, end_date):
        """Generate a group biweekly report for a period"""
        try:
            # Check if report already exists for the period
            existing_report = GroupAIReport.objects.filter(
                group_id=group_id,
                report_period_start=start_date,
                report_period_end=end_date
            ).first()
            
            if existing_report:
                logger.info(f"Biweekly report for group {group_id} from {start_date} to {end_date} already exists")
                return existing_report
            
            # Get transactions within the period
            transactions = GroupTransaction.objects.filter(
                group_id=group_id,
                transaction_date__date__gte=start_date,
                transaction_date__date__lte=end_date
            ).select_related('category', 'subcategory', 'user')
            
            if not transactions.exists():
                logger.info(f"Group {group_id} has no transactions between {start_date} and {end_date}")
                return self._create_empty_biweekly_report(group_id, start_date, end_date)
            
            # Analyze transactions ！！wrapper method call for generic method _analyze_transactions_base(...)
            analysis_data = self._analyze_group_transactions(transactions)
            
            # Generate report content! wrapper method call for generic method _generate_report_content_base(...)
            report_content = self._generate_biweekly_report_content(analysis_data, start_date, end_date)
            
            # Save report ！！wrapper method call for generic method _save_report(...)
            report = self._save_biweekly_report(group_id, report_content, analysis_data, start_date, end_date)
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate group biweekly report: {str(e)}")
            return self._create_error_biweekly_report(group_id, start_date, end_date, str(e))
    
    def _analyze_group_transactions(self, transactions):
        """Analyze group transactions"""
        return self._analyze_transactions_base(transactions, include_user_info=True)
    
    def _generate_report_content(self, analysis_data):
        """Generate report content"""
        return self._generate_report_content_base(analysis_data, self._build_analysis_prompt)
    
    def _build_analysis_prompt(self, analysis_data):
        """Build analysis prompt"""
        return self._build_base_analysis_prompt(analysis_data)
    
    def _generate_biweekly_report_content(self, analysis_data, start_date, end_date):
        """Generate biweekly report content"""
        return self._generate_report_content_base(analysis_data, 
            lambda data: self._build_biweekly_analysis_prompt(data, start_date, end_date))
    
     # !!!Build "period information " , Group information and the period information and focus points specific to the biweekly report
    #    and pass it to the _build_base_analysis_prompt(...)
    def _build_biweekly_analysis_prompt(self, analysis_data, start_date, end_date):
        """Build biweekly analysis prompt"""
        period_info = f"- Analysis period: {start_date} to {end_date}"
        base_prompt = self._build_base_analysis_prompt(analysis_data, period_info)
        
        # Add team biweekly specific requirements
        biweekly_specific = f"""
**Team Biweekly Analysis Focus:**
- Analyze team spending patterns within this specific 2-week period
- Compare with typical team spending patterns
- Identify any unusual team spending behavior during this period
- Provide period-specific team recommendations
- Consider team collaboration and shared financial goals
"""
        
        return base_prompt + biweekly_specific
    
    def _save_report(self, group_id, report_content, analysis_data, analysis_period_days):
        """Save report"""
        report_data = {
            'group_id': group_id,
            'financial_advice_summary': report_content['financial_advice_summary'],
            'abnormal_alert': report_content['abnormal_alert'],
            'money_saving_tip': report_content['money_saving_tip'],
            'analysis_period': f"Last {analysis_period_days} days",
            'total_transactions': analysis_data['total_transactions'],
            'total_amount': analysis_data['total_amount'],
            'is_generated': True,
            'generation_status': 'completed'
        }
        
        return self._create_report(GroupAIReport, report_data)
    
    def _create_empty_report(self, group_id, analysis_period_days):
        """Create an empty report"""
        empty_content = {
            'financial_advice_summary': f"Your team's financial health assessment for the last {analysis_period_days} days shows no recorded spending activity. This could indicate excellent team financial discipline, incomplete expense tracking, or a period of minimal team spending. To gain better financial insights, consider implementing a comprehensive team expense tracking system.",
            'abnormal_alert': f"No team spending data available for the {analysis_period_days}-day analysis period. This may indicate either excellent team financial control or a need to improve team expense tracking habits.",
            'money_saving_tip': f"Since no team spending data is available for the last {analysis_period_days} days, focus on establishing robust team financial habits: 1) **Team Setup**: Implement shared expense tracking using apps like Splitwise, Venmo, or shared spreadsheets; 2) **Team Budget Framework**: Create a collaborative 50/30/20 budget for team expenses; 3) **Team Emergency Fund**: Establish a team emergency fund for shared expenses; 4) **Expense Categories**: Set up team categories for meals, transportation, entertainment, and utilities; 5) **Tracking Commitment**: Commit to tracking all team expenses for at least 30 days; 6) **Team Financial Goals**: Set specific, measurable team financial goals with timelines; 7) **Automation**: Set up automatic team savings transfers; 8) **Regular Team Reviews**: Schedule weekly team spending reviews; 9) **Team Subscription Audit**: Review and optimize team subscriptions and shared services; 10) **Team Future Planning**: Consider long-term team financial planning and investment strategies."
        }
        
        report_data = {
            'group_id': group_id,
            'financial_advice_summary': empty_content['financial_advice_summary'],
            'abnormal_alert': empty_content['abnormal_alert'],
            'money_saving_tip': empty_content['money_saving_tip'],
            'analysis_period': f"Last {analysis_period_days} days",
            'total_transactions': 0,
            'total_amount': 0,
            'is_generated': True,
            'generation_status': 'completed'
        }
        
        return self._create_report(GroupAIReport, report_data)
    
    def _create_error_report(self, group_id, analysis_period_days, error_message):
        """Create an error report"""
        error_content = {
            'financial_advice_summary': "Report generation failed. Please try again later.",
            'abnormal_alert': "System error. Please contact administrator.",
            'money_saving_tip': "Due to system issues, detailed advice is temporarily unavailable. Please manually check team spending patterns."
        }
        
        report_data = {
            'group_id': group_id,
            'financial_advice_summary': error_content['financial_advice_summary'],
            'abnormal_alert': error_content['abnormal_alert'],
            'money_saving_tip': error_content['money_saving_tip'],
            'analysis_period': f"Last {analysis_period_days} days",
            'total_transactions': 0,
            'total_amount': 0,
            'is_generated': False,
            'generation_status': 'failed'
        }
        
        report = self._create_report(GroupAIReport, report_data, is_generated=False, generation_status='failed')
        logger.error(f"Error report created for group {group_id}, error: {error_message}")
        return report
    
    def _save_biweekly_report(self, group_id, report_content, analysis_data, start_date, end_date):
        """Save biweekly report"""
        period_name = f"{start_date} to {end_date}"
        
        report_data = {
            'group_id': group_id,
            'financial_advice_summary': report_content['financial_advice_summary'],
            'abnormal_alert': report_content['abnormal_alert'],
            'money_saving_tip': report_content['money_saving_tip'],
            'analysis_period': f"{start_date} to {end_date}",
            'total_transactions': analysis_data['total_transactions'],
            'total_amount': analysis_data['total_amount'],
            'is_generated': True,
            'generation_status': 'completed',
            'report_period_start': start_date,
            'report_period_end': end_date,
            'period_name': period_name
        }
        
        return self._create_report(GroupAIReport, report_data)
    
    def _create_empty_biweekly_report(self, group_id, start_date, end_date):
        """Create an empty biweekly report"""
        period_name = f"{start_date} to {end_date}"
        empty_content = {
            'financial_advice_summary': "No transaction data available for this period.",
            'abnormal_alert': "No anomalies detected.",
            'money_saving_tip': "Consider starting to track team expenses during this period to build good financial habits."
        }
        
        report_data = {
            'group_id': group_id,
            'financial_advice_summary': empty_content['financial_advice_summary'],
            'abnormal_alert': empty_content['abnormal_alert'],
            'money_saving_tip': empty_content['money_saving_tip'],
            'analysis_period': f"{start_date} to {end_date}",
            'total_transactions': 0,
            'total_amount': 0,
            'is_generated': True,
            'generation_status': 'completed',
            'report_period_start': start_date,
            'report_period_end': end_date,
            'period_name': period_name
        }
        
        return self._create_report(GroupAIReport, report_data)
    
    def _create_error_biweekly_report(self, group_id, start_date, end_date, error_message):
        """Create an error biweekly report"""
        period_name = f"{start_date} to {end_date}"
        error_content = {
            'financial_advice_summary': "Report generation failed. Please try again later.",
            'abnormal_alert': "System error. Please contact administrator.",
            'money_saving_tip': "Due to system issues, detailed advice is temporarily unavailable. Please manually check team spending patterns."
        }
        
        report_data = {
            'group_id': group_id,
            'financial_advice_summary': error_content['financial_advice_summary'],
            'abnormal_alert': error_content['abnormal_alert'],
            'money_saving_tip': error_content['money_saving_tip'],
            'analysis_period': f"{start_date} to {end_date}",
            'total_transactions': 0,
            'total_amount': 0,
            'is_generated': False,
            'generation_status': 'failed',
            'report_period_start': start_date,
            'report_period_end': end_date,
            'period_name': period_name
        }
        
        report = self._create_report(GroupAIReport, report_data, is_generated=False, generation_status='failed')
        logger.error(f"Error biweekly report created for group {group_id}, error: {error_message}")
        return report
