from django.contrib import admin
from .models import GmailToken, Email

@admin.register(GmailToken)
class GmailTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    
    def has_add_permission(self, request):
        return False  # 不允许手动添加，只能通过API创建

@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ['subject', 'sender', 'user', 'received_at', 'is_read']
    list_filter = ['is_read', 'received_at', 'user']
    search_fields = ['subject', 'sender', 'body', 'user__username']
    readonly_fields = ['gmail_id', 'thread_id', 'created_at', 'updated_at']
    date_hierarchy = 'received_at'
    
    def get_queryset(self, request):
        """只显示当前用户的邮件（如果是普通用户）"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)
