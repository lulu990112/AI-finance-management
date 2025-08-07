import openai
import logging
from django.conf import settings
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta, date
from .models import Transaction, Category, Subcategory, AIReport
import json

logger = logging.getLogger(__name__)

class AIReportGenerator:
    """AI理财报告生成器"""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def generate_report(self, user, analysis_period_days=30):
        """生成用户的AI理财报告"""
        try:
            # 获取用户的交易数据
            end_date = timezone.now()
            start_date = end_date - timedelta(days=analysis_period_days)
            
            transactions = Transaction.objects.filter(
                user=user,
                transaction_date__gte=start_date,
                transaction_date__lte=end_date
            ).select_related('category', 'subcategory')
            
            if not transactions.exists():
                return self._create_empty_report(user, analysis_period_days)
            
            # 分析交易数据
            analysis_data = self._analyze_transactions(transactions)
            
            # 生成报告内容
            report_content = self._generate_report_content(analysis_data)
            
            # 保存报告
            report = self._save_report(user, report_content, analysis_data, analysis_period_days)
            
            return report
            
        except Exception as e:
            logger.error(f"生成AI报告失败: {str(e)}")
            return self._create_error_report(user, analysis_period_days, str(e))
    
    def generate_biweekly_report(self, user, start_date, end_date):
        """生成指定时间段的半个月报告"""
        try:
            # 检查是否已有该周期的报告
            existing_report = AIReport.objects.filter(
                user=user,
                report_type='biweekly',
                report_period_start=start_date,
                report_period_end=end_date
            ).first()
            
            if existing_report:
                logger.info(f"用户 {user.username} 的 {start_date} 到 {end_date} 的半个月报告已存在")
                return existing_report
            
            # 获取指定时间段的交易数据
            transactions = Transaction.objects.filter(
                user=user,
                transaction_date__date__gte=start_date,
                transaction_date__date__lte=end_date
            ).select_related('category', 'subcategory')
            
            if not transactions.exists():
                logger.info(f"用户 {user.username} 在 {start_date} 到 {end_date} 期间没有交易数据")
                return self._create_empty_biweekly_report(user, start_date, end_date)
            
            # 分析交易数据
            analysis_data = self._analyze_transactions(transactions)
            
            # 生成报告内容
            report_content = self._generate_biweekly_report_content(analysis_data, start_date, end_date)
            
            # 保存报告
            report = self._save_biweekly_report(user, report_content, analysis_data, start_date, end_date)
            
            return report
            
        except Exception as e:
            logger.error(f"生成半个月报告失败: {str(e)}")
            return self._create_error_biweekly_report(user, start_date, end_date, str(e))
    
    def calculate_biweekly_periods(self, user):
        """计算用户的半个月报告周期"""
        try:
            # 获取用户第一个交易
            first_transaction = Transaction.objects.filter(user=user).order_by('transaction_date').first()
            if not first_transaction:
                logger.info(f"用户 {user.username} 没有交易数据")
                return []
            
            start_date = first_transaction.transaction_date.date()
            current_date = timezone.now().date()
            
            periods = []
            current_period_start = start_date
            
            while current_period_start <= current_date:
                # 计算半个月后的日期
                if current_period_start.day <= 15:
                    # 上半月：1-15号
                    current_period_end = current_period_start.replace(day=15)
                else:
                    # 下半月：16号到月底
                    if current_period_start.month == 12:
                        current_period_end = current_period_start.replace(year=current_period_start.year + 1, month=1, day=1) - timedelta(days=1)
                    else:
                        current_period_end = current_period_start.replace(month=current_period_start.month + 1, day=1) - timedelta(days=1)
                
                periods.append({
                    'start_date': current_period_start,
                    'end_date': current_period_end,
                    'period_name': f"{current_period_start.strftime('%Y-%m-%d')} to {current_period_end.strftime('%Y-%m-%d')}"
                })
                
                # 计算下一个周期开始日期
                current_period_start = current_period_end + timedelta(days=1)
            
            return periods
            
        except Exception as e:
            logger.error(f"计算半个月周期失败: {str(e)}")
            return []
    
    def _analyze_transactions(self, transactions):
        """分析交易数据"""
        analysis = {
            'total_transactions': transactions.count(),
            'total_amount': float(transactions.aggregate(total=Sum('amount'))['total'] or 0),
            'category_breakdown': {},
            'subcategory_breakdown': {},
            'monthly_spending': {},
            'high_value_transactions': [],
            'frequent_vendors': {},
            'spending_patterns': {}
        }
        
        # 按分类统计
        category_stats = transactions.values('category__name').annotate(
            count=Count('id'),
            total=Sum('amount')
        )
        
        for stat in category_stats:
            category_name = stat['category__name']
            analysis['category_breakdown'][category_name] = {
                'count': stat['count'],
                'total': float(stat['total']),
                'percentage': 0
            }
        
        # 按子分类统计
        subcategory_stats = transactions.values('subcategory__name', 'subcategory__category__name').annotate(
            count=Count('id'),
            total=Sum('amount')
        )
        
        for stat in subcategory_stats:
            subcategory_name = stat['subcategory__name']
            category_name = stat['subcategory__category__name']
            analysis['subcategory_breakdown'][subcategory_name] = {
                'count': stat['count'],
                'total': float(stat['total']),
                'category': category_name
            }
        
        # 计算百分比
        total_amount = analysis['total_amount']
        if total_amount > 0:
            for category_data in analysis['category_breakdown'].values():
                category_data['percentage'] = (category_data['total'] / total_amount) * 100
        
        # 识别高价值交易（超过平均值的2倍）
        avg_amount = total_amount / analysis['total_transactions'] if analysis['total_transactions'] > 0 else 0
        high_value_threshold = avg_amount * 2
        
        for transaction in transactions:
            if float(transaction.amount) > high_value_threshold:
                analysis['high_value_transactions'].append({
                    'amount': float(transaction.amount),
                    'vendor': transaction.vendor,
                    'category': transaction.category.name,
                    'date': transaction.transaction_date.strftime('%Y-%m-%d')
                })
        
        # 统计频繁商家
        vendor_stats = transactions.values('vendor').annotate(
            count=Count('id'),
            total=Sum('amount')
        ).order_by('-count')[:10]
        
        for stat in vendor_stats:
            analysis['frequent_vendors'][stat['vendor']] = {
                'count': stat['count'],
                'total': float(stat['total'])
            }
        
        return analysis
    
    def _generate_report_content(self, analysis_data):
        """使用GPT生成报告内容"""
        prompt = self._build_analysis_prompt(analysis_data)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional financial advisor with expertise in personal finance management, budgeting, and financial planning. You analyze spending patterns, identify financial risks, and provide actionable, personalized financial advice. Your recommendations should be practical, specific, and based on actual spending data."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            
            # 解析GPT返回的内容
            return self._parse_report_content(content)
            
        except Exception as e:
            logger.error(f"GPT生成报告失败: {str(e)}")
            return self._generate_fallback_report(analysis_data)
    
    def _build_analysis_prompt(self, analysis_data):
        """构建分析提示词"""
        # 计算平均值
        avg_amount = analysis_data['total_amount'] / analysis_data['total_transactions'] if analysis_data['total_transactions'] > 0 else 0
        
        prompt = f"""
You are a professional financial advisor with expertise in personal finance management. Analyze the following spending data and provide a comprehensive financial report in English with exactly three sections.

**Financial Analysis Task:**
Analyze the user's spending patterns, identify potential financial risks, and provide actionable advice for improving financial health.

**Spending Data Overview:**
- Total transactions: {analysis_data['total_transactions']}
- Total amount: ${analysis_data['total_amount']:.2f}
- Average transaction amount: ${avg_amount:.2f}

**Detailed Spending Analysis:**

**Category Breakdown:**
"""
        
        for category, data in analysis_data['category_breakdown'].items():
            prompt += f"- {category}: ${data['total']:.2f} ({data['percentage']:.1f}%) - {data['count']} transactions\n"
        
        prompt += f"""
**Top Subcategories (by spending):**
"""
        
        # 添加前5个子分类
        sorted_subcategories = sorted(
            analysis_data['subcategory_breakdown'].items(),
            key=lambda x: x[1]['total'],
            reverse=True
        )[:5]
        
        for subcategory, data in sorted_subcategories:
            prompt += f"- {subcategory}: ${data['total']:.2f} ({data['category']})\n"
        
        if analysis_data['high_value_transactions']:
            prompt += f"""
**High-Value Transactions (over ${analysis_data['high_value_transactions'][0]['amount']:.2f}):**
"""
            for transaction in analysis_data['high_value_transactions'][:3]:
                prompt += f"- {transaction['vendor']}: ${transaction['amount']:.2f} ({transaction['category']}) - {transaction['date']}\n"
        
        # 添加频繁商家分析
        if analysis_data['frequent_vendors']:
            prompt += f"""
**Frequent Vendors:**
"""
            for vendor, data in list(analysis_data['frequent_vendors'].items())[:5]:
                prompt += f"- {vendor}: {data['count']} transactions, ${data['total']:.2f}\n"
        
        prompt += f"""
**Analysis Framework:**

**1. Spending Distribution Analysis:**
- Primary spending categories: {', '.join(list(analysis_data['category_breakdown'].keys())[:3])}
- Highest expense category: {max(analysis_data['category_breakdown'].items(), key=lambda x: x[1]['total'])[0] if analysis_data['category_breakdown'] else 'N/A'}
- Spending concentration: {'High' if max([data['percentage'] for data in analysis_data['category_breakdown'].values()]) > 50 else 'Moderate' if max([data['percentage'] for data in analysis_data['category_breakdown'].values()]) > 30 else 'Diversified'} concentration in top category

**2. Financial Health Indicators:**
- Transaction frequency: {'High' if analysis_data['total_transactions'] > 50 else 'Moderate' if analysis_data['total_transactions'] > 20 else 'Low'} ({analysis_data['total_transactions']} transactions)
- Average transaction size: {'High' if avg_amount > 100 else 'Moderate' if avg_amount > 50 else 'Low'} (${avg_amount:.2f})
- High-value transaction ratio: {len(analysis_data['high_value_transactions'])} out of {analysis_data['total_transactions']} transactions

**3. Risk Assessment:**
- Spending volatility: {'High' if len(analysis_data['high_value_transactions']) > analysis_data['total_transactions'] * 0.1 else 'Moderate' if len(analysis_data['high_value_transactions']) > analysis_data['total_transactions'] * 0.05 else 'Low'}
- Category diversification: {'Poor' if len(analysis_data['category_breakdown']) < 3 else 'Good' if len(analysis_data['category_breakdown']) < 5 else 'Excellent'}

**Report Structure Requirements:**

**1. Financial Advice Summary (50-80 words):**
- Overall financial health assessment based on spending patterns
- Key recommendations for immediate improvement
- Priority areas for financial focus
- Consider spending distribution, transaction frequency, and average amounts

**2. Abnormal Alert (20-40 words):**
- Identify unusual spending patterns or concerning trends
- Highlight potential financial risks or red flags
- Focus on high-value transactions, category concentration, or spending volatility
- Provide specific concerns that need immediate attention

**3. Money Saving Tip (250-350 words):**
- Provide detailed, actionable money-saving advice based on spending patterns
- Include specific strategies for the highest expense categories
- Suggest budget recommendations and spending controls
- Offer practical examples and implementation steps
- Consider long-term financial planning and goal setting
- Address specific spending habits identified in the analysis

**Analysis Guidelines:**
- Focus on actionable and practical advice
- Consider the user's spending priorities and patterns
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
- Ensure all advice is practical and implementable
- Base recommendations on actual spending data provided
- Provide specific, measurable suggestions
- Consider the user's financial situation holistically
- Focus on sustainable financial habits
"""
        
        return prompt
    
    def _parse_report_content(self, content):
        """解析GPT返回的报告内容"""
        sections = {
            'financial_advice_summary': '',
            'abnormal_alert': '',
            'money_saving_tip': ''
        }
        
        try:
            lines = content.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if line.startswith('Financial Advice Summary:'):
                    current_section = 'financial_advice_summary'
                elif line.startswith('Abnormal Alert:'):
                    current_section = 'abnormal_alert'
                elif line.startswith('Money Saving Tip:'):
                    current_section = 'money_saving_tip'
                elif current_section and line:
                    sections[current_section] += line + ' '
            
            # 清理和截断内容
            for key in sections:
                sections[key] = sections[key].strip()
                if len(sections[key]) > 1000:  # 增加到1000字符，确保300字的Money Saving Tip能够完整显示
                    sections[key] = sections[key][:1000] + '...'
            
            return sections
            
        except Exception as e:
            logger.error(f"解析报告内容失败: {str(e)}")
            return self._generate_fallback_report({})
    
    def _generate_fallback_report(self, analysis_data):
        """生成备用报告"""
        return {
            'financial_advice_summary': 'Based on your spending data, consider reviewing your budget and identifying areas for potential savings.',
            'abnormal_alert': 'No significant anomalies detected in your recent spending patterns.',
            'money_saving_tip': 'Consider tracking your daily expenses and setting up automatic savings transfers. Review your subscription services regularly and cancel unused ones. Look for opportunities to reduce spending in your highest expense categories.'
        }
    
    def _save_report(self, user, report_content, analysis_data, analysis_period_days):
        """保存报告到数据库"""
        report = AIReport.objects.create(
            user=user,
            financial_advice_summary=report_content['financial_advice_summary'],
            abnormal_alert=report_content['abnormal_alert'],
            money_saving_tip=report_content['money_saving_tip'],
            analysis_period=f"Last {analysis_period_days} days",
            total_transactions=analysis_data['total_transactions'],
            total_amount=analysis_data['total_amount'],
            is_generated=True,
            generation_status='completed'
        )
        
        return report
    
    def _create_empty_report(self, user, analysis_period_days):
        """创建空报告（无交易数据时）"""
        report = AIReport.objects.create(
            user=user,
            financial_advice_summary='No spending data available for analysis.',
            abnormal_alert='No transactions found in the specified period.',
            money_saving_tip='Start tracking your expenses to receive personalized financial advice. Consider setting up a budget and monitoring your spending habits regularly.',
            analysis_period=f"Last {analysis_period_days} days",
            total_transactions=0,
            total_amount=0,
            is_generated=True,
            generation_status='completed'
        )
        
        return report
    
    def _create_error_report(self, user, analysis_period_days, error_message):
        """创建错误报告"""
        report = AIReport.objects.create(
            user=user,
            financial_advice_summary='Unable to generate financial advice at this time.',
            abnormal_alert='Report generation encountered an error.',
            money_saving_tip='Please try again later or contact support if the issue persists.',
            analysis_period=f"Last {analysis_period_days} days",
            total_transactions=0,
            total_amount=0,
            is_generated=False,
            generation_status='failed'
        )
        
        return report 
    
    def _generate_biweekly_report_content(self, analysis_data, start_date, end_date):
        """使用GPT生成半个月报告内容"""
        prompt = self._build_biweekly_analysis_prompt(analysis_data, start_date, end_date)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional financial advisor with expertise in personal finance management, budgeting, and financial planning. You analyze spending patterns, identify financial risks, and provide actionable, personalized financial advice. Your recommendations should be practical, specific, and based on actual spending data."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            
            # 解析GPT返回的内容
            return self._parse_report_content(content)
            
        except Exception as e:
            logger.error(f"GPT生成半个月报告失败: {str(e)}")
            return self._generate_fallback_biweekly_report(analysis_data, start_date, end_date)
    
    def _build_biweekly_analysis_prompt(self, analysis_data, start_date, end_date):
        """构建半个月分析提示词"""
        period_days = (end_date - start_date).days + 1
        
        # 计算平均值
        avg_amount = analysis_data['total_amount'] / analysis_data['total_transactions'] if analysis_data['total_transactions'] > 0 else 0
        daily_avg = analysis_data['total_amount'] / period_days
        
        prompt = f"""
You are a professional financial advisor with expertise in personal finance management. Analyze the following biweekly spending data and provide a comprehensive financial report in English with exactly three sections.

**Biweekly Financial Analysis Task:**
Analyze the user's spending patterns for the period {start_date} to {end_date} ({period_days} days), identify potential financial risks, and provide actionable advice for improving financial health.

**Spending Data Overview:**
- Analysis period: {start_date} to {end_date} ({period_days} days)
- Total transactions: {analysis_data['total_transactions']}
- Total amount: ${analysis_data['total_amount']:.2f}
- Average transaction amount: ${avg_amount:.2f}
- Daily average spending: ${daily_avg:.2f}

**Detailed Spending Analysis:**

**Category Breakdown:**
"""
        
        for category, data in analysis_data['category_breakdown'].items():
            prompt += f"- {category}: ${data['total']:.2f} ({data['percentage']:.1f}%) - {data['count']} transactions\n"
        
        prompt += f"""
**Top Subcategories (by spending):**
"""
        
        # 添加前5个子分类
        sorted_subcategories = sorted(
            analysis_data['subcategory_breakdown'].items(),
            key=lambda x: x[1]['total'],
            reverse=True
        )[:5]
        
        for subcategory, data in sorted_subcategories:
            prompt += f"- {subcategory}: ${data['total']:.2f} ({data['category']})\n"
        
        if analysis_data['high_value_transactions']:
            prompt += f"""
**High-Value Transactions (over ${analysis_data['high_value_transactions'][0]['amount']:.2f}):**
"""
            for transaction in analysis_data['high_value_transactions'][:3]:
                prompt += f"- {transaction['vendor']}: ${transaction['amount']:.2f} ({transaction['category']}) - {transaction['date']}\n"
        
        # 添加频繁商家分析
        if analysis_data['frequent_vendors']:
            prompt += f"""
**Frequent Vendors:**
"""
            for vendor, data in list(analysis_data['frequent_vendors'].items())[:5]:
                prompt += f"- {vendor}: {data['count']} transactions, ${data['total']:.2f}\n"
        
        prompt += f"""
**Biweekly Analysis Framework:**

**1. Spending Distribution Analysis:**
- Primary spending categories: {', '.join(list(analysis_data['category_breakdown'].keys())[:3])}
- Highest expense category: {max(analysis_data['category_breakdown'].items(), key=lambda x: x[1]['total'])[0] if analysis_data['category_breakdown'] else 'N/A'}
- Spending concentration: {'High' if max([data['percentage'] for data in analysis_data['category_breakdown'].values()]) > 50 else 'Moderate' if max([data['percentage'] for data in analysis_data['category_breakdown'].values()]) > 30 else 'Diversified'} concentration in top category

**2. Financial Health Indicators:**
- Transaction frequency: {'High' if analysis_data['total_transactions'] > 20 else 'Moderate' if analysis_data['total_transactions'] > 10 else 'Low'} ({analysis_data['total_transactions']} transactions in {period_days} days)
- Average transaction size: {'High' if avg_amount > 100 else 'Moderate' if avg_amount > 50 else 'Low'} (${avg_amount:.2f})
- Daily spending average: ${daily_avg:.2f}
- High-value transaction ratio: {len(analysis_data['high_value_transactions'])} out of {analysis_data['total_transactions']} transactions

**3. Risk Assessment:**
- Spending volatility: {'High' if len(analysis_data['high_value_transactions']) > analysis_data['total_transactions'] * 0.1 else 'Moderate' if len(analysis_data['high_value_transactions']) > analysis_data['total_transactions'] * 0.05 else 'Low'}
- Category diversification: {'Poor' if len(analysis_data['category_breakdown']) < 3 else 'Good' if len(analysis_data['category_breakdown']) < 5 else 'Excellent'}

**Report Structure Requirements:**

**1. Financial Advice Summary (50-80 words):**
- Overall financial health assessment for this biweekly period
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
- Suggest budget recommendations and spending controls for the next biweekly period
- Offer practical examples and implementation steps
- Consider long-term financial planning and goal setting
- Address specific spending habits identified in the analysis

**Analysis Guidelines:**
- Focus on actionable and practical advice for biweekly periods
- Consider the user's spending priorities and patterns in this specific timeframe
- Provide specific examples when possible
- Use professional but accessible language
- Consider both short-term and long-term financial goals
- Address potential financial risks and opportunities
- Suggest realistic and achievable recommendations for the next biweekly period

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
    
    def _parse_report_content(self, content):
        """解析GPT返回的报告内容"""
        sections = {
            'financial_advice_summary': '',
            'abnormal_alert': '',
            'money_saving_tip': ''
        }
        
        try:
            lines = content.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if line.startswith('Financial Advice Summary:'):
                    current_section = 'financial_advice_summary'
                elif line.startswith('Abnormal Alert:'):
                    current_section = 'abnormal_alert'
                elif line.startswith('Money Saving Tip:'):
                    current_section = 'money_saving_tip'
                elif current_section and line:
                    sections[current_section] += line + ' '
            
            # 清理和截断内容
            for key in sections:
                sections[key] = sections[key].strip()
                if len(sections[key]) > 1000:  # 增加到1000字符，确保300字的Money Saving Tip能够完整显示
                    sections[key] = sections[key][:1000] + '...'
            
            return sections
            
        except Exception as e:
            logger.error(f"解析报告内容失败: {str(e)}")
            return self._generate_fallback_report({})
    
    def _generate_fallback_report(self, analysis_data):
        """生成备用报告"""
        return {
            'financial_advice_summary': 'Based on your spending data, consider reviewing your budget and identifying areas for potential savings.',
            'abnormal_alert': 'No significant anomalies detected in your recent spending patterns.',
            'money_saving_tip': 'Consider tracking your daily expenses and setting up automatic savings transfers. Review your subscription services regularly and cancel unused ones. Look for opportunities to reduce spending in your highest expense categories.'
        }
    
    def _save_biweekly_report(self, user, report_content, analysis_data, start_date, end_date):
        """保存半个月报告到数据库"""
        period_name = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        
        report = AIReport.objects.create(
            user=user,
            financial_advice_summary=report_content['financial_advice_summary'],
            abnormal_alert=report_content['abnormal_alert'],
            money_saving_tip=report_content['money_saving_tip'],
            analysis_period=f"Biweekly period: {period_name}",
            total_transactions=analysis_data['total_transactions'],
            total_amount=analysis_data['total_amount'],
            is_generated=True,
            generation_status='completed',
            report_type='biweekly',
            report_period_start=start_date,
            report_period_end=end_date,
            period_name=period_name
        )
        
        return report
    
    def _create_empty_biweekly_report(self, user, start_date, end_date):
        """创建空半个月报告（无交易数据时）"""
        period_name = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        
        report = AIReport.objects.create(
            user=user,
            financial_advice_summary='No spending data available for this biweekly period.',
            abnormal_alert='No transactions found in this period.',
            money_saving_tip='Start tracking your expenses to receive personalized financial advice. Consider setting up a budget and monitoring your spending habits regularly for the next biweekly period.',
            analysis_period=f"Biweekly period: {period_name}",
            total_transactions=0,
            total_amount=0,
            is_generated=True,
            generation_status='completed',
            report_type='biweekly',
            report_period_start=start_date,
            report_period_end=end_date,
            period_name=period_name
        )
        
        return report
    
    def _create_error_biweekly_report(self, user, start_date, end_date, error_message):
        """创建错误半个月报告"""
        period_name = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        
        report = AIReport.objects.create(
            user=user,
            financial_advice_summary='Unable to generate financial advice for this biweekly period.',
            abnormal_alert='Report generation encountered an error.',
            money_saving_tip='Please try again later or contact support if the issue persists.',
            analysis_period=f"Biweekly period: {period_name}",
            total_transactions=0,
            total_amount=0,
            is_generated=False,
            generation_status='failed',
            report_type='biweekly',
            report_period_start=start_date,
            report_period_end=end_date,
            period_name=period_name
        )
        
        return report
    
    def _generate_fallback_biweekly_report(self, analysis_data, start_date, end_date):
        """生成备用半个月报告"""
        return {
            'financial_advice_summary': f'Based on your spending data from {start_date} to {end_date}, consider reviewing your budget and identifying areas for potential savings.',
            'abnormal_alert': 'No significant anomalies detected in your biweekly spending patterns.',
            'money_saving_tip': f'For the period {start_date} to {end_date}, consider tracking your daily expenses and setting up automatic savings transfers. Review your subscription services regularly and cancel unused ones. Look for opportunities to reduce spending in your highest expense categories. Plan your budget for the next biweekly period based on this analysis.'
        } 