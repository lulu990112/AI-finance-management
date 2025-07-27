from django.db import models



class GmailToken(models.Model):
    """存储用户的Gmail授权令牌，确保每个用户只有一个令牌"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='gmail_token')
    access_token = models.TextField()
    refresh_token = models.TextField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
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
            return json.loads(self.recipients)
        except:
            return [self.recipients]
