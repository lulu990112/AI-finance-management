from django.contrib import admin
from .models import GmailToken, Email, Transaction, Category, Subcategory, AIReport, Group, GroupTransaction, GroupAIReport

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
        """Only show transactions for the current user (if not superuser)"""
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
        return False  # Not allowed to add manually, only through API

@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ['subject', 'sender', 'user', 'received_at', 'is_read']
    list_filter = ['is_read', 'received_at', 'user']
    search_fields = ['subject', 'sender', 'body', 'user__username']
    readonly_fields = ['gmail_id', 'thread_id', 'created_at', 'updated_at']
    date_hierarchy = 'received_at'
    
    def get_queryset(self, request):
        """Only show emails for the current user"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

@admin.register(AIReport)
class AIReportAdmin(admin.ModelAdmin):
    list_display = ['user', 'report_date', 'analysis_period', 'total_transactions', 'total_amount', 'is_generated', 'generation_status']
    list_filter = ['is_generated', 'generation_status', 'report_date']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['report_date', 'total_transactions', 'total_amount']
    ordering = ['-report_date']

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['group_id', 'group_name', 'user', 'role', 'member_count', 'created_at']
    list_filter = ['role', 'created_at', 'group_id']
    search_fields = ['group_name', 'user__username', 'description']
    readonly_fields = ['joined_at', 'created_at']
    ordering = ['-created_at']
    
    def member_count(self, obj):
        """Show the number of group members"""
        return Group.objects.filter(group_id=obj.group_id).count()
    member_count.short_description = 'Member count'

@admin.register(GroupTransaction)
class GroupTransactionAdmin(admin.ModelAdmin):
    list_display = ['group_transaction_id', 'group_id', 'user', 'item_name', 'amount', 'vendor', 'category', 'transaction_date', 'is_manual']
    list_filter = ['group_id', 'category', 'is_manual', 'transaction_date', 'source']
    search_fields = ['item_name', 'vendor', 'user__username', 'note']
    readonly_fields = ['group_transaction_id', 'created_at']
    ordering = ['-transaction_date']

@admin.register(GroupAIReport)
class GroupAIReportAdmin(admin.ModelAdmin):
    list_display = ['group_ai_report_id', 'group_id', 'report_date', 'analysis_period', 'total_transactions', 'total_amount', 'is_generated', 'generation_status']
    list_filter = ['is_generated', 'generation_status', 'report_date', 'group_id']
    search_fields = ['analysis_period', 'period_name']
    readonly_fields = ['group_ai_report_id', 'report_date']
    ordering = ['-report_date']
