"""
ai_report_service.py

This module generates AI financial reports for individual users based on their transactions.

The service is responsible for:
- Fetching and filtering a user's transactions for a given period (recent N days or a biweekly window)
- Analyzing spending data via shared utilities and building the analysis prompt
- Producing report content with the LLM and structuring it into three sections
- Persisting `AIReport` records and deduplicating by period
- Handling empty datasets and error scenarios with fallback reports
- Calculating continuous biweekly periods from the user's first transaction
"""

import logging
from django.utils import timezone
from datetime import timedelta, date
from .models import Transaction, AIReport
from .base_ai_report_service import BaseAIReportGenerator

logger = logging.getLogger(__name__)

# class Child(Parent) ！！！
class AIReportGenerator(BaseAIReportGenerator):
    """AI financial report generator"""
    
    def generate_report(self, user, analysis_period_days=30):
        """Generate an AI financial report for the user"""
        try:
            # Get user's transactions for the analysis period
            end_date = timezone.now()
            start_date = end_date - timedelta(days=analysis_period_days)
            
            transactions = Transaction.objects.filter(
                user=user,
                transaction_date__gte=start_date,
                transaction_date__lte=end_date
            ).select_related('category', 'subcategory')
            
            if not transactions.exists():
                return self._create_empty_report(user, analysis_period_days)
            
            # Analyze transactions ！！wrapper method call for generic method _analyze_transactions_base(...)
            analysis_data = self._analyze_transactions(transactions)
            
            # Generate report content! wrapper method call for generic method _generate_report_content_base(...)
            report_content = self._generate_report_content(analysis_data)
            
            # Save report ！！wrapper method call for generic method _save_report(...)
            report = self._save_report(user, report_content, analysis_data, analysis_period_days)
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate AI report: {str(e)}")
            return self._create_error_report(user, analysis_period_days, str(e))
    
    def generate_biweekly_report(self, user, start_date, end_date):
        """Generate a biweekly report for the specified period"""
        try:
            # Check if a report for this period already exists
            existing_report = AIReport.objects.filter(
                user=user,
                report_type='biweekly',
                report_period_start=start_date,
                report_period_end=end_date
            ).first()
            
            if existing_report:
                logger.info(f"Biweekly report for user {user.username} from {start_date} to {end_date} already exists")
                return existing_report
            
            # Get transactions within the specified period
            transactions = Transaction.objects.filter(
                user=user,
                transaction_date__date__gte=start_date,
                transaction_date__date__lte=end_date
            ).select_related('category', 'subcategory')
            
            if not transactions.exists():
                logger.info(f"No transactions for user {user.username} between {start_date} and {end_date}")
                return self._create_empty_biweekly_report(user, start_date, end_date)
            
            # Analyze transactions ！！wrapper method call for generic method _analyze_transactions_base(...)
            analysis_data = self._analyze_transactions(transactions)
            
            # Generate report content! wrapper method call for generic method _generate_report_content_base(...)
            report_content = self._generate_biweekly_report_content(analysis_data, start_date, end_date)
            
            # Save report ！！wrapper method call for generic method _save_report(...)
            report = self._save_biweekly_report(user, report_content, analysis_data, start_date, end_date)
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate biweekly report: {str(e)}")
            return self._create_error_biweekly_report(user, start_date, end_date, str(e))
    
    def calculate_biweekly_periods(self, user):
        """Calculate biweekly report periods for the user"""
        try:
            # Get the user's first transaction
            first_transaction = Transaction.objects.filter(user=user).order_by('transaction_date').first()
            if not first_transaction:
                logger.info(f"User {user.username} has no transaction data")
                return []
            
            start_date = first_transaction.transaction_date.date()
            current_date = timezone.now().date()
            
            periods = []
            current_period_start = start_date
            
            while current_period_start <= current_date:
                # Compute the date 14 days later
                current_period_end = min(
                    current_period_start + timedelta(days=14),
                    current_date
                )
                
                periods.append({
                    'start_date': current_period_start,
                    'end_date': current_period_end,
                    'period_name': f"{current_period_start} to {current_period_end}"
                })
                
                # Move to the next period
                current_period_start = current_period_end + timedelta(days=1)
            
            return periods
            
        except Exception as e:
            logger.error(f"Failed to calculate biweekly periods: {str(e)}")
            return []
    

    #！！This is how to override the base class method！
    def _analyze_transactions(self, transactions):
        """Analyze transactions"""
        return self._analyze_transactions_base(transactions, include_user_info=False)
    
    def _generate_report_content(self, analysis_data):
        """Generate report content"""
        return self._generate_report_content_base(analysis_data, self._build_analysis_prompt)
    
    def _build_analysis_prompt(self, analysis_data):
        """Build analysis prompt"""
        return self._build_base_analysis_prompt(analysis_data)
        
    # !!!Build "period information " and pass it to the _generate_report_content_base(...)
    def _generate_biweekly_report_content(self, analysis_data, start_date, end_date):
        """Generate biweekly report content"""
        return self._generate_report_content_base(analysis_data, 
            lambda data: self._build_biweekly_analysis_prompt(data, start_date, end_date))
    
    # !!!Build the period information and focus points specific to the biweekly report
    #    and pass it to the _build_base_analysis_prompt(...)
    def _build_biweekly_analysis_prompt(self, analysis_data, start_date, end_date):
        """Build biweekly analysis prompt"""
        period_info = f"- Analysis period: {start_date} to {end_date}"
        base_prompt = self._build_base_analysis_prompt(analysis_data, period_info)
        
        # Add biweekly-specific analysis requirements
        biweekly_specific = f"""
**Biweekly Analysis Focus:**
- Analyze spending patterns within this specific 2-week period
- Compare with typical spending patterns
- Identify any unusual spending behavior during this period
- Provide period-specific recommendations
"""
        
        return base_prompt + biweekly_specific
    
    def _save_report(self, user, report_content, analysis_data, analysis_period_days):
        """Save report"""
        report_data = {
            'user': user,
            'financial_advice_summary': report_content['financial_advice_summary'],
            'abnormal_alert': report_content['abnormal_alert'],
            'money_saving_tip': report_content['money_saving_tip'],
            'analysis_period': f"Last {analysis_period_days} days",
            'total_transactions': analysis_data['total_transactions'],
            'total_amount': analysis_data['total_amount'],
            'is_generated': True,
            'generation_status': 'completed'
        }
        
        return self._create_report(AIReport, report_data)
    
    def _create_empty_report(self, user, analysis_period_days):
        """Create an empty report"""
        empty_content = {
            'financial_advice_summary': f"Your financial health assessment for the last {analysis_period_days} days shows no recorded spending activity. This could indicate excellent financial discipline, incomplete expense tracking, or a period of minimal spending. To gain better financial insights, consider implementing a comprehensive expense tracking system.",
            'abnormal_alert': f"No spending data available for the {analysis_period_days}-day analysis period. This may indicate either excellent financial control or a need to improve expense tracking habits.",
            'money_saving_tip': f"Since no spending data is available for the last {analysis_period_days} days, focus on establishing robust financial habits: 1) **Immediate Setup**: Install expense tracking apps like Mint, YNAB, or Personal Capital; 2) **Budget Framework**: Create a 50/30/20 budget (50% needs, 30% wants, 20% savings); 3) **Emergency Fund**: Start building a 3-6 month emergency fund; 4) **Expense Categories**: Set up categories for housing, food, transportation, entertainment, and utilities; 5) **Tracking Commitment**: Commit to tracking all expenses for at least 30 days; 6) **Financial Goals**: Set specific, measurable financial goals with timelines; 7) **Automation**: Set up automatic savings transfers; 8) **Regular Reviews**: Schedule weekly spending reviews; 9) **Subscription Audit**: Review and cancel unnecessary subscriptions; 10) **Future Planning**: Consider long-term financial planning and investment strategies."
        }
        
        report_data = {
            'user': user,
            'financial_advice_summary': empty_content['financial_advice_summary'],
            'abnormal_alert': empty_content['abnormal_alert'],
            'money_saving_tip': empty_content['money_saving_tip'],
            'analysis_period': f"Last {analysis_period_days} days",
            'total_transactions': 0,
            'total_amount': 0,
            'is_generated': True,
            'generation_status': 'completed'
        }
        
        return self._create_report(AIReport, report_data)
    
    def _create_error_report(self, user, analysis_period_days, error_message):
        """Create an error report"""
        error_content = {
            'financial_advice_summary': "Report generation failed. Please try again later.",
            'abnormal_alert': "System error. Please contact administrator.",
            'money_saving_tip': "Due to system issues, detailed advice is temporarily unavailable. Please manually check your spending patterns."
        }
        
        report_data = {
            'user': user,
            'financial_advice_summary': error_content['financial_advice_summary'],
            'abnormal_alert': error_content['abnormal_alert'],
            'money_saving_tip': error_content['money_saving_tip'],
            'analysis_period': f"Last {analysis_period_days} days",
            'total_transactions': 0,
            'total_amount': 0,
            'is_generated': False,
            'generation_status': 'failed'
        }
        
        report = self._create_report(AIReport, report_data, is_generated=False, generation_status='failed')
        logger.error(f"Error report created for user {user.username}, error: {error_message}")
        return report
    
    def _save_biweekly_report(self, user, report_content, analysis_data, start_date, end_date):
        """Save biweekly report"""
        period_name = f"{start_date} to {end_date}"
        
        report_data = {
            'user': user,
            'financial_advice_summary': report_content['financial_advice_summary'],
            'abnormal_alert': report_content['abnormal_alert'],
            'money_saving_tip': report_content['money_saving_tip'],
            'analysis_period': f"{start_date} to {end_date}",
            'total_transactions': analysis_data['total_transactions'],
            'total_amount': analysis_data['total_amount'],
            'is_generated': True,
            'generation_status': 'completed',
            'report_type': 'biweekly',
            'report_period_start': start_date,
            'report_period_end': end_date,
            'period_name': period_name
        }
        
        return self._create_report(AIReport, report_data)
    
    def _create_empty_biweekly_report(self, user, start_date, end_date):
        """Create an empty biweekly report"""
        period_name = f"{start_date} to {end_date}"
        empty_content = {
            'financial_advice_summary': "No transaction data available for this period.",
            'abnormal_alert': "No anomalies detected.",
            'money_saving_tip': "Consider starting to track your expenses during this period to build good financial habits."
        }
        
        report_data = {
            'user': user,
            'financial_advice_summary': empty_content['financial_advice_summary'],
            'abnormal_alert': empty_content['abnormal_alert'],
            'money_saving_tip': empty_content['money_saving_tip'],
            'analysis_period': f"{start_date} to {end_date}",
            'total_transactions': 0,
            'total_amount': 0,
            'is_generated': True,
            'generation_status': 'completed',
            'report_type': 'biweekly',
            'report_period_start': start_date,
            'report_period_end': end_date,
            'period_name': period_name
        }
        
        return self._create_report(AIReport, report_data)
    
    def _create_error_biweekly_report(self, user, start_date, end_date, error_message):
        """Create an error biweekly report"""
        period_name = f"{start_date} to {end_date}"
        error_content = {
            'financial_advice_summary': "Report generation failed. Please try again later.",
            'abnormal_alert': "System error. Please contact administrator.",
            'money_saving_tip': "Due to system issues, detailed advice is temporarily unavailable. Please manually check your spending patterns."
        }
        
        report_data = {
            'user': user,
            'financial_advice_summary': error_content['financial_advice_summary'],
            'abnormal_alert': error_content['abnormal_alert'],
            'money_saving_tip': error_content['money_saving_tip'],
            'analysis_period': f"{start_date} to {end_date}",
            'total_transactions': 0,
            'total_amount': 0,
            'is_generated': False,
            'generation_status': 'failed',
            'report_type': 'biweekly',
            'report_period_start': start_date,
            'report_period_end': end_date,
            'period_name': period_name
        }
        
        report = self._create_report(AIReport, report_data, is_generated=False, generation_status='failed')
        logger.error(f"Error biweekly report created for user {user.username}, error: {error_message}")
        return report 