from django.db import models
from django.contrib.auth.models import User
import json


class GmailToken(models.Model):
    """存储用户的Gmail授权令牌，确保每个用户只有一个令牌"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='gmail_token')
    access_token = models.TextField()
    refresh_token = models.TextField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    last_sync_time = models.DateTimeField(null=True, blank=True)  # 记录上次同步时间
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'gmail_token'

    def __str__(self):
        return f"Gmail Token for {self.user.username}"

class Email(models.Model):
    """存储用户的邮件信息，通过user字段关联到特定用户"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='emails')
    gmail_id = models.CharField(max_length=100)  # Gmail的邮件ID
    thread_id = models.CharField(max_length=100)  # Gmail的线程ID
    subject = models.CharField(max_length=500, null=True, blank=True)
    sender = models.CharField(max_length=255)
    recipients = models.TextField()  # JSON格式存储收件人列表
    body = models.TextField(null=True, blank=True)
    snippet = models.TextField(null=True, blank=True)
    received_at = models.DateTimeField()
    is_read = models.BooleanField(default=False)
    labels = models.TextField()  # JSON格式存储Gmail标签
    is_processed = models.BooleanField(default=False)  # 标记是否已被GPT处理
    processed_at = models.DateTimeField(null=True, blank=True)  # 处理时间
    last_sync_time = models.DateTimeField(null=True, blank=True)  # 记录邮件同步时间
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'email'
        # 确保同一用户的同一邮件不会重复存储
        unique_together = ['user', 'gmail_id']

    def __str__(self):
        return f"Email: {self.subject} - {self.user.username}"

    def get_labels_list(self):
        """获取标签列表"""
        try:
            return json.loads(self.labels)
        except:
            return []

    def get_recipients_list(self):
        """获取收件人列表"""
        try:
            recipients = json.loads(self.recipients)
            return recipients if recipients else [self.recipients]
        except:
            return [self.recipients]

class Category(models.Model):
    """交易主分类"""
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

class Subcategory(models.Model):
    """交易子分类"""
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default='#000000')  # 颜色代码，如 #FF0000
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'subcategory'
        verbose_name_plural = 'Subcategories'
        unique_together = ['category', 'name']  # 同一分类下子分类名称唯一

    def __str__(self):
        return f"{self.category.name} - {self.name}"

class Transaction(models.Model):
    """交易记录 - 每个商品对应一个Transaction"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    email = models.ForeignKey(Email, on_delete=models.CASCADE, related_name='transactions', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='transactions')
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE, related_name='transactions')
    
    # 单个商品信息
    item_name = models.CharField(max_length=255, default='Unknown Item')  # 商品名称
    item_brand = models.CharField(max_length=100, null=True, blank=True)  # 品牌
    item_quantity = models.IntegerField(default=1)  # 数量
    item_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # 单价
    item_description = models.TextField(null=True, blank=True)  # 商品描述
    
    # 交易信息
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # 总金额（单价 × 数量）
    currency = models.CharField(max_length=3, default='USD')  # 货币代码
    vendor = models.CharField(max_length=255)  # 商家名称
    transaction_date = models.DateTimeField()  # 交易日期
    source = models.CharField(max_length=50, default='email')  # 数据来源：email
    note = models.TextField(null=True, blank=True)  # 备注信息
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'transaction'
        ordering = ['-transaction_date']

    def __str__(self):
        return f"{self.vendor} - {self.item_name} - {self.amount} {self.currency}"

    def save(self, *args, **kwargs):
        # 自动计算总金额
        if not self.amount:
            self.amount = self.item_unit_price * self.item_quantity
        super().save(*args, **kwargs)

    def get_item_info(self):
        """获取商品信息字典"""
        return {
            'name': self.item_name,
            'brand': self.item_brand,
            'quantity': self.item_quantity,
            'unit_price': float(self.item_unit_price),
            'description': self.item_description
        }

class AIReport(models.Model):
    """AI生成的理财报告"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_reports')
    
    # 报告的三个部分
    financial_advice_summary = models.TextField()  # 理财建议总结（约50字）
    abnormal_alert = models.TextField()  # 异常警报（约30字）
    money_saving_tip = models.TextField()  # 省钱建议（约300字）
    
    # 报告元数据
    report_date = models.DateTimeField(auto_now_add=True)  # 报告生成时间
    analysis_period = models.CharField(max_length=50)  # 分析周期（如"最近30天"）
    total_transactions = models.IntegerField()  # 分析的交易总数
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)  # 总金额
    
    # 报告状态
    is_generated = models.BooleanField(default=False)  # 是否已生成
    generation_status = models.CharField(max_length=20, default='pending')  # 生成状态：pending, processing, completed, failed
    
    # 新增字段：支持半个月报告
    report_type = models.CharField(max_length=20, default='general', choices=[
        ('general', '通用报告'),
        ('biweekly', '半个月报告'),
        ('monthly', '月度报告'),
    ])  # 报告类型
    report_period_start = models.DateField(null=True, blank=True)  # 报告周期开始日期
    report_period_end = models.DateField(null=True, blank=True)  # 报告周期结束日期
    period_name = models.CharField(max_length=100, null=True, blank=True)  # 周期名称（如"2024-01-01 to 2024-01-15"）
    
    class Meta:
        db_table = 'ai_report'
        ordering = ['-report_date']
        # 确保同一用户的同一周期只有一份报告
        unique_together = ['user', 'report_type', 'report_period_start', 'report_period_end']

    def __str__(self):
        if self.report_type == 'biweekly' and self.period_name:
            return f"Biweekly AI Report for {self.user.username} - {self.period_name}"
        return f"AI Report for {self.user.username} - {self.report_date.strftime('%Y-%m-%d')}"

    def get_report_data(self):
        """获取报告数据字典"""
        return {
            'id': self.id,
            'financial_advice_summary': self.financial_advice_summary,
            'abnormal_alert': self.abnormal_alert,
            'money_saving_tip': self.money_saving_tip,
            'report_date': self.report_date.isoformat(),
            'analysis_period': self.analysis_period,
            'total_transactions': self.total_transactions,
            'total_amount': str(self.total_amount),
            'is_generated': self.is_generated,
            'generation_status': self.generation_status,
            'report_type': self.report_type,
            'report_period_start': self.report_period_start.isoformat() if self.report_period_start else None,
            'report_period_end': self.report_period_end.isoformat() if self.report_period_end else None,
            'period_name': self.period_name,
        }
