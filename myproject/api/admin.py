from django.contrib import admin
from .models import GmailToken, Email, Transaction, Category, Subcategory

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']
    readonly_fields = ['created_at']

@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'color', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'category__name']
    readonly_fields = ['created_at']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['item_name', 'vendor', 'amount', 'currency', 'category', 'subcategory', 'user', 'transaction_date']
    list_filter = ['category', 'subcategory', 'currency', 'transaction_date', 'user']
    search_fields = ['item_name', 'vendor', 'user__username', 'category__name', 'subcategory__name']
    readonly_fields = ['created_at']
    date_hierarchy = 'transaction_date'
    
    def get_queryset(self, request):
        """只显示当前用户的交易（如果是普通用户）"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

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
