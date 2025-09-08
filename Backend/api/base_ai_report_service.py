"""
base_ai_report_service.py

This module provides the shared foundation used by report generators. It wraps
common behaviors so feature modules can focus on business logic.

The service is responsible for:
- Computing descriptive analytics from transactions (totals, averages, breakdowns)
- Building rich LLM prompts from the analytics context
- Calling the OpenAI API and parsing structured sections from responses
- Providing robust fallbacks when model calls or parsing fail
- Persisting report entities in a consistent way for different report types
"""

import openai
import logging
from django.conf import settings
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta, date
import json

logger = logging.getLogger(__name__)

class BaseAIReportGenerator:
    """Base class for AI report generation with common utilities"""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def _create_report(self, report_model, report_data, is_generated=True, generation_status='completed'):
        """Common helper: create a report"""
        try:
            report = report_model.objects.create(**report_data)
            status_text = "success" if is_generated else "error"
            logger.info(f"AI report generation {status_text}")
            return report
        except Exception as e:
            logger.error(f"Failed to create AI report: {str(e)}")
            raise
    
    def _analyze_transactions_base(self, transactions, include_user_info=False):
        """Common helper: analyze transactions"""
        try:
            # Basic statistics
            total_amount = transactions.aggregate(total=Sum('amount'))['total'] or 0
            total_count = transactions.count()
            avg_amount = transactions.aggregate(avg=Sum('amount') / Count('amount'))['avg'] or 0
            
            # Category breakdown
            category_stats = transactions.values('category__name').annotate(
                total_amount=Sum('amount'),
                transaction_count=Count('amount')
            ).order_by('-total_amount')
            
            # Subcategory breakdown
            subcategory_stats = transactions.values(
                'category__name', 
                'subcategory__name', 
                'subcategory__color'
            ).annotate(
                total_amount=Sum('amount'),
                transaction_count=Count('amount')
            ).order_by('-total_amount')
            
            # Vendor statistics (enhanced)
            vendor_stats = transactions.values('vendor').annotate(
                total_amount=Sum('amount'),
                transaction_count=Count('amount'),
                avg_amount=Sum('amount') / Count('amount')
            ).order_by('-total_amount')[:15]
            
            # Time dimension analysis
            daily_stats = transactions.extra(
                select={'date': 'DATE(transaction_date)'}
            ).values('date').annotate(
                total_amount=Sum('amount'),
                transaction_count=Count('amount'),
                avg_amount=Sum('amount') / Count('amount')
            ).order_by('-total_amount')[:10]
            
            # Weekly analysis (simplified for now)
            weekly_stats = []
            
            # High-value transaction analysis (enhanced)
            high_value_threshold = float(avg_amount) * 2
            high_value_transactions = transactions.filter(amount__gt=high_value_threshold)
            
            # Collect details for high-value transactions
            high_value_details = []
            for transaction in high_value_transactions:
                high_value_details.append({
                    'amount': float(transaction.amount),
                    'vendor': transaction.vendor,
                    'item_name': transaction.item_name,
                    'category': transaction.category.name,
                    'date': transaction.transaction_date.strftime('%Y-%m-%d'),
                    'user': transaction.user.username if hasattr(transaction, 'user') else 'N/A'
                })
            
            # Anomaly pattern detection
            # 1) Single-day high spending
            daily_high_spending = []
            for day_stat in daily_stats:
                if day_stat['total_amount'] > float(total_amount) / 7:  # > 7x average daily spending
                    daily_high_spending.append({
                        'date': day_stat['date'],
                        'amount': float(day_stat['total_amount']),
                        'transactions': day_stat['transaction_count']
                    })
            
            # 2) Frequent vendors
            frequent_vendors = []
            for vendor_stat in vendor_stats:
                if vendor_stat['transaction_count'] > 3:  # more than 3 transactions
                    frequent_vendors.append({
                        'vendor': vendor_stat['vendor'],
                        'total_amount': float(vendor_stat['total_amount']),
                        'transaction_count': vendor_stat['transaction_count'],
                        'avg_amount': float(vendor_stat['avg_amount'])
                    })
            
            # 3) Spending concentration analysis
            category_concentration = {}
            for category in category_stats:
                percentage = (category['total_amount'] / total_amount * 100) if total_amount > 0 else 0
                category_concentration[category['category__name']] = {
                    'percentage': percentage,
                    'total_amount': float(category['total_amount']),
                    'transaction_count': category['transaction_count']
                }
            
            # 4) Spending pattern summary
            spending_patterns = {
                'daily_average': float(total_amount) / max(len(daily_stats), 1),
                'transaction_frequency': float(total_count) / max(len(daily_stats), 1),
                'high_value_ratio': (high_value_transactions.count() / total_count * 100) if total_count > 0 else 0,
                'vendor_diversity': len(vendor_stats),
                'category_diversity': len(category_stats)
            }
            
            analysis_data = {
                'total_transactions': total_count,
                'total_amount': float(total_amount),
                'average_amount': float(avg_amount),
                'category_breakdown': list(category_stats),
                'subcategory_breakdown': list(subcategory_stats),
                'vendor_breakdown': list(vendor_stats),
                'daily_breakdown': list(daily_stats),
                'weekly_breakdown': list(weekly_stats),
                'high_value_transactions': high_value_details,
                'high_value_count': high_value_transactions.count(),
                'high_value_threshold': float(high_value_threshold),
                'daily_high_spending': daily_high_spending,
                'frequent_vendors': frequent_vendors,
                'category_concentration': category_concentration,
                'spending_patterns': spending_patterns
            }
            
            # Add user breakdown if needed
            if include_user_info:
                user_stats = transactions.values('user__username').annotate(
                    total_amount=Sum('amount'),
                    transaction_count=Count('amount'),
                    avg_amount=Sum('amount') / Count('amount')
                ).order_by('-total_amount')
                analysis_data['user_breakdown'] = list(user_stats)
            
            return analysis_data
            
        except Exception as e:
            logger.error(f"Failed to analyze transactions: {str(e)}")
            raise
    
    def _generate_report_content_base(self, analysis_data, prompt_builder_func):
        """Common helper: generate report content"""
        try:
            # Build analysis prompt
            prompt = prompt_builder_func(analysis_data)
            
            # Call OpenAI API !!
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional financial advisor with expertise in personal finance management. Analyze the following spending data and provide a comprehensive financial report in English with exactly three sections."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            
            # Parse model output into structured sections
            report_content = self._parse_report_content_base(content)
            
            return report_content
            
        except Exception as e:
            logger.error(f"Failed to generate report content: {str(e)}")
            # Fallback to heuristic content
            return self._generate_fallback_report_base(analysis_data)
    
    def _parse_report_content_base(self, content):
        """Common helper: parse report content"""
        try:
            # Try to parse structured report sections
            sections = {
                'financial_advice_summary': '',
                'abnormal_alert': '',
                'money_saving_tip': ''
            }
            
            lines = content.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                if 'Financial Advice Summary:' in line:
                    current_section = 'financial_advice_summary'
                    sections[current_section] = line.replace('Financial Advice Summary:', '').strip()
                elif 'Abnormal Alert:' in line:
                    current_section = 'abnormal_alert'
                    sections[current_section] = line.replace('Abnormal Alert:', '').strip()
                elif 'Money Saving Tip:' in line:
                    current_section = 'money_saving_tip'
                    sections[current_section] = line.replace('Money Saving Tip:', '').strip()
                elif current_section and line:
                    sections[current_section] += ' ' + line
            
            # Ensure all sections have content
            for key, value in sections.items():
                if not value.strip():
                    sections[key] = f"Default {key.replace('_', ' ').title()}"
            
            return sections
            
        except Exception as e:
            logger.error(f"Failed to parse report content: {str(e)}")
            return self._generate_fallback_report_base({})
    
    def _generate_fallback_report_base(self, analysis_data):
        """Common helper: generate a fallback report"""
        total_amount = analysis_data.get('total_amount', 0)
        total_transactions = analysis_data.get('total_transactions', 0)
        
        if total_transactions == 0:
            return {
                'financial_advice_summary': "Your financial health assessment shows no recent spending activity. This could indicate either excellent financial discipline or a need to track expenses more regularly. Consider establishing a comprehensive expense tracking system.",
                'abnormal_alert': "No spending data available for analysis. This may indicate either excellent financial control or incomplete expense tracking.",
                'money_saving_tip': "Since no spending data is available, focus on establishing good financial habits: 1) Set up automatic expense tracking using apps like Mint or YNAB; 2) Create a monthly budget with specific categories (housing 30%, food 15%, transportation 10%, etc.); 3) Build an emergency fund of 3-6 months' expenses; 4) Review and cancel unnecessary subscriptions; 5) Consider using cash-back credit cards for purchases; 6) Set up automatic savings transfers; 7) Track all expenses for at least 30 days to identify spending patterns; 8) Set specific financial goals with timelines."
            }
        
        avg_amount = total_amount / total_transactions if total_transactions > 0 else 0
        spending_level = "low" if total_amount < 100 else "moderate" if total_amount < 500 else "high"
        
        # Gather details for personalized suggestions
        category_breakdown = analysis_data.get('category_breakdown', [])
        vendor_breakdown = analysis_data.get('vendor_breakdown', [])
        daily_high_spending = analysis_data.get('daily_high_spending', [])
        frequent_vendors = analysis_data.get('frequent_vendors', [])
        
        # Construct personalized advice
        top_category = category_breakdown[0]['category__name'] if category_breakdown else 'general expenses'
        top_vendor = vendor_breakdown[0]['vendor'] if vendor_breakdown else 'various vendors'
        
        # Identify specific issues
        specific_issues = []
        if daily_high_spending:
            specific_issues.append(f"unusual high spending on {daily_high_spending[0]['date']} (${daily_high_spending[0]['amount']:.2f})")
        if frequent_vendors:
            specific_issues.append(f"frequent spending at {frequent_vendors[0]['vendor']} ({frequent_vendors[0]['transaction_count']} transactions)")
        if avg_amount > 100:
            specific_issues.append(f"high average transaction amount (${avg_amount:.2f})")
        
        issues_text = "; ".join(specific_issues) if specific_issues else "no concerning patterns detected"
        
        return {
            'financial_advice_summary': f"Your financial health assessment shows {spending_level} spending activity with ${total_amount:.2f} across {total_transactions} transactions. Your average transaction of ${avg_amount:.2f} indicates {'conservative' if avg_amount < 50 else 'moderate' if avg_amount < 100 else 'generous'} spending habits. Primary spending focus is on {top_category} with frequent transactions at {top_vendor}. Focus on optimizing your highest expense categories and consider implementing a structured budget to improve financial efficiency.",
            'abnormal_alert': f"Analysis shows {total_transactions} transactions totaling ${total_amount:.2f} with an average of ${avg_amount:.2f} per transaction. {issues_text}.",
            'money_saving_tip': f"Based on your spending of ${total_amount:.2f} across {total_transactions} transactions, here are personalized strategies: 1) **Immediate Actions**: Review all transactions and identify 3 unnecessary expenses to eliminate; 2) **Budget Planning**: Allocate 50% for needs, 30% for wants, 20% for savings; 3) **Specific Savings**: Reduce average transaction from ${avg_amount:.2f} to ${avg_amount * 0.8:.2f} by comparing prices; 4) **Technology Tools**: Use apps like Mint, YNAB, or Personal Capital for tracking; 5) **Emergency Fund**: Save ${total_amount * 0.1:.2f} monthly toward 3-6 months' expenses; 6) **Negotiation**: Contact service providers to reduce recurring costs; 7) **Alternative Options**: Research cheaper alternatives for frequent purchases; 8) **Behavioral Changes**: Implement 24-hour rule for purchases over ${avg_amount:.2f}; 9) **Long-term Planning**: Set up automatic savings and investment contributions; 10) **Regular Review**: Schedule weekly spending reviews to maintain accountability."
        }
    
    def _build_base_analysis_prompt(self, analysis_data, period_info=""):
        """Common helper: build base analysis prompt"""
        
        # Key metrics
        total_amount = analysis_data['total_amount']
        total_transactions = analysis_data['total_transactions']
        avg_amount = analysis_data['average_amount']
        
        # Daily average window
        period_days = 30  # default 30 days; adjust if explicit period provided
        if period_info and "to" in period_info:
            try:
                start_str, end_str = period_info.split(" to ")
                start_date = datetime.strptime(start_str.strip(), "%Y-%m-%d")
                end_date = datetime.strptime(end_str.strip(), "%Y-%m-%d")
                period_days = (end_date - start_date).days + 1
            except:
                pass
        
        daily_avg = total_amount / period_days if period_days > 0 else 0
        
        # Spending pattern labels
        spending_pattern = "Low" if total_amount < 100 else "Moderate" if total_amount < 500 else "High"
        transaction_frequency = "Low" if total_transactions < 5 else "Moderate" if total_transactions < 15 else "High"
        
        # Top categories
        top_categories = [cat['category__name'] for cat in analysis_data['category_breakdown'][:3]]
        highest_category = analysis_data['category_breakdown'][0]['category__name'] if analysis_data['category_breakdown'] else 'N/A'
        highest_percentage = (float(analysis_data['category_breakdown'][0]['total_amount']) / total_amount * 100) if analysis_data['category_breakdown'] and total_amount > 0 else 0
        
        # High-value transaction ratio
        high_value_ratio = (analysis_data['high_value_count'] / total_transactions * 100) if total_transactions > 0 else 0
        
        prompt = f"""
You are a professional financial advisor with expertise in personal finance management, budgeting, and financial planning. You analyze spending patterns, identify financial risks, and provide actionable, personalized financial advice. Your recommendations should be practical, specific, and based on actual spending data.

**Financial Analysis Task:**
Analyze the user's spending patterns for the period {period_info if period_info else "Recent period"}, identify potential financial risks, and provide actionable advice for improving financial health.

**Spending Data Overview:**
- Analysis period: {period_info if period_info else "Recent period"}
- Total transactions: {total_transactions}
- Total amount: ${total_amount:.2f}
- Average transaction amount: ${avg_amount:.2f}
- Daily average spending: ${daily_avg:.2f}

**Detailed Spending Analysis:**

**Category Breakdown:**
"""
        
        for i, category in enumerate(analysis_data['category_breakdown']):
            percentage = (float(category['total_amount']) / total_amount * 100) if total_amount > 0 else 0
            prompt += f"- {category['category__name']}: ${category['total_amount']:.2f} ({percentage:.1f}%) - {category['transaction_count']} transactions\n"
        
        if analysis_data['subcategory_breakdown']:
            prompt += f"""
**Top Subcategories (by spending):**
"""
            for i, subcategory in enumerate(analysis_data['subcategory_breakdown'][:5]):
                prompt += f"- {subcategory['subcategory__name']}: ${subcategory['total_amount']:.2f} ({subcategory['category__name']})\n"
        
        if analysis_data['high_value_transactions']:
            prompt += f"""
**High-Value Transactions (over ${analysis_data['high_value_threshold']:.2f}):**
"""
            for transaction in analysis_data['high_value_transactions'][:3]:
                prompt += f"- {transaction['vendor']}: ${transaction['amount']:.2f} ({transaction['category']}) - {transaction['date']}\n"
        
        # Add frequent vendor analysis
        if analysis_data['frequent_vendors']:
            prompt += f"""
**Frequent Vendors:**
"""
            for vendor in analysis_data['frequent_vendors'][:5]:
                prompt += f"- {vendor['vendor']}: {vendor['transaction_count']} transactions, ${vendor['total_amount']:.2f}\n"
        
        # Add time dimension analysis
        if analysis_data['daily_breakdown']:
            prompt += f"""
**Daily Spending Analysis (Top 5 Days):**
"""
            for i, day in enumerate(analysis_data['daily_breakdown'][:5]):
                prompt += f"- {day['date']}: ${day['total_amount']:.2f} ({day['transaction_count']} transactions, avg: ${day['avg_amount']:.2f})\n"
        
        # Add daily high spending analysis
        if analysis_data['daily_high_spending']:
            prompt += f"""
**Unusual High-Spending Days:**
"""
            for day in analysis_data['daily_high_spending']:
                prompt += f"- {day['date']}: ${day['amount']:.2f} ({day['transactions']} transactions) - This day shows unusually high spending\n"
        
        prompt += f"""
**Financial Analysis Framework:**

**1. Spending Distribution Analysis:**
- Primary spending categories: {', '.join(top_categories)}
- Highest expense category: {highest_category}
- Spending concentration: {'High' if highest_percentage > 50 else 'Moderate' if highest_percentage > 30 else 'Diversified'} concentration in top category

**2. Financial Health Indicators:**
- Transaction frequency: {'High' if total_transactions > 20 else 'Moderate' if total_transactions > 10 else 'Low'} ({total_transactions} transactions)
- Average transaction size: {'High' if avg_amount > 100 else 'Moderate' if avg_amount > 50 else 'Low'} (${avg_amount:.2f})
- Daily spending average: ${daily_avg:.2f}
- High-value transaction ratio: {analysis_data['high_value_count']} out of {total_transactions} transactions

**3. Risk Assessment:**
- Spending volatility: {'High' if len(analysis_data['high_value_transactions']) > total_transactions * 0.1 else 'Moderate' if len(analysis_data['high_value_transactions']) > total_transactions * 0.05 else 'Low'}
- Category diversification: {'Poor' if len(analysis_data['category_breakdown']) < 3 else 'Good' if len(analysis_data['category_breakdown']) < 5 else 'Excellent'}

**Report Structure Requirements:**

**1. Financial Advice Summary (50-80 words):**
- Overall financial health assessment for this period
- Key recommendations for immediate improvement
- Priority areas for financial focus
- Consider spending distribution, transaction frequency, and daily averages

**2. Abnormal Alert (20-40 words):**
- Identify unusual spending patterns or concerning trends in this period
- Highlight potential financial risks or red flags
- Focus on high-value transactions, category concentration, or spending volatility
- Provide specific concerns that need immediate attention

**3. Money Saving Tip (250-350 words):**
- Provide detailed, actionable money-saving advice based on this period's spending patterns
- Include specific strategies for the highest expense categories
- Suggest budget recommendations and spending controls for the next period
- Offer practical examples and implementation steps
- Consider long-term financial planning and goal setting
- Address specific spending habits identified in the analysis

**Analysis Guidelines:**
- Focus on actionable and practical advice
- Consider the user's spending priorities and patterns in this specific timeframe
- Provide specific examples when possible
- Use professional but accessible language
- Consider both short-term and long-term financial goals
- Address potential financial risks and opportunities
- Suggest realistic and achievable recommendations

**Output Format:**
```
Financial Advice Summary:
[Your comprehensive summary here]

Abnormal Alert:
[Your specific alert here]

Money Saving Tip:
[Your detailed, actionable advice here]
```

**Quality Requirements:**
- Ensure all advice is practical and implementable for biweekly periods
- Base recommendations on actual spending data provided for this period
- Provide specific, measurable suggestions
- Consider the user's financial situation holistically
- Focus on sustainable financial habits
"""
        
        return prompt
