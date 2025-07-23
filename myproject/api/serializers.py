from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email

class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True, validators=[validate_email])
    password = serializers.CharField(write_only=True, required=True, min_length=6, validators=[validate_password])
    confirmPassword = serializers.CharField(write_only=True, required=True, label="确认密码")

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'confirmPassword')

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('用户名已被占用。')
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('邮箱已被占用。')
        return value

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('confirmPassword'):
            raise serializers.ValidationError({'confirmPassword': '两次输入的密码不一致。'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirmPassword')  # 移除 confirmPassword 字段
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)
