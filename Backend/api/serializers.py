"""
serializers.py

This module defines a collection of Django REST Framework (DRF) serializers that handle user authentication, group management, financial transactions, and AI-generated reports.
The serializers are responsible for:

- Validating incoming request data
- Transforming database models into structured API responses
- Managing nested relationships such as groups, transactions, and categories
"""

from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email
from .models import Group, GroupTransaction, GroupAIReport, Transaction, Category, Subcategory

class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True, validators=[validate_email])
    password = serializers.CharField(write_only=True, required=True, min_length=6, validators=[validate_password])
    confirmPassword = serializers.CharField(write_only=True, required=True, label="Confirm password")

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'confirmPassword')

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Username is already taken.')
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email is already taken.')
        return value

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('confirmPassword'):
            raise serializers.ValidationError({'confirmPassword': 'Two input passwords are inconsistent.'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirmPassword')  # Remove confirmPassword field
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)

# Serializers for group-related features
class GroupSerializer(serializers.ModelSerializer):
    """Group information serializer"""
    group_name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)
    max_members = serializers.IntegerField(default=10, min_value=1, max_value=50)
    member_count = serializers.SerializerMethodField()
    owner_username = serializers.SerializerMethodField()
    
    class Meta:
        model = Group
        fields = ('group_id', 'group_name', 'description', 'max_members', 'role', 
                 'joined_at', 'created_at', 'member_count', 'owner_username')
        read_only_fields = ('group_id', 'joined_at', 'created_at', 'member_count', 'owner_username')
    
    def get_member_count(self, obj):
        """Get member count"""
        return Group.objects.filter(group_id=obj.group_id).count()
    
    def get_owner_username(self, obj):
        """Get owner username"""
        owner = Group.objects.filter(group_id=obj.group_id, role='owner').first()
        return owner.user.username if owner else None

class GroupCreateSerializer(serializers.Serializer):
    """Group creation serializer"""
    group_name = serializers.CharField(max_length=255, required=True)
    description = serializers.CharField(required=False, allow_blank=True)
    max_members = serializers.IntegerField(default=10, min_value=1, max_value=50)

class GroupMemberSerializer(serializers.ModelSerializer):
    """Group member serializer"""
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = Group
        fields = ('user', 'username', 'email', 'role', 'joined_at')
        read_only_fields = ('user', 'username', 'email', 'joined_at')

class GroupJoinSerializer(serializers.Serializer):
    """Group join serializer"""
    group_id = serializers.IntegerField(required=True)

class TransactionShareSerializer(serializers.Serializer):
    """Transaction sharing serializer"""
    transaction_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True,
        help_text="List of transaction IDs to share"
    )
    group_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True,
        help_text="List of group IDs to share to"
    )

class GroupTransactionSerializer(serializers.ModelSerializer):
    """Group transaction serializer"""
    username = serializers.CharField(source='user.username', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    subcategory_name = serializers.CharField(source='subcategory.name', read_only=True)
    subcategory_color = serializers.CharField(source='subcategory.color', read_only=True)
    
    class Meta:
        model = GroupTransaction
        fields = ('group_transaction_id', 'group_id', 'original_transaction', 'user', 'username',
                 'category', 'category_name', 'subcategory', 'subcategory_name', 'subcategory_color',
                 'item_name', 'item_brand', 'item_quantity', 'item_unit_price', 'item_description',
                 'amount', 'currency', 'vendor', 'transaction_date', 'source', 'note',
                 'is_manual', 'created_at')
        read_only_fields = ('group_transaction_id', 'created_at')

class GroupAIReportSerializer(serializers.ModelSerializer):
    """Group AI report serializer"""
    
    class Meta:
        model = GroupAIReport
        fields = ('group_ai_report_id', 'group_id', 'financial_advice_summary', 'abnormal_alert',
                 'money_saving_tip', 'report_date', 'analysis_period', 'total_transactions',
                 'total_amount', 'is_generated', 'generation_status', 'report_period_start',
                 'report_period_end', 'period_name')
        read_only_fields = ('group_ai_report_id', 'report_date')

class CategorySerializer(serializers.ModelSerializer):
    """Category serializer"""
    
    class Meta:
        model = Category
        fields = ('id', 'name')

class SubcategorySerializer(serializers.ModelSerializer):
    """Subcategory serializer"""
    
    class Meta:
        model = Subcategory
        fields = ('id', 'category', 'name', 'color')
