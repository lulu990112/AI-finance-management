
import os
import requests
from django.conf import settings
from django.shortcuts import redirect
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, LoginSerializer

@api_view(['POST'])
def register(request):
    # Pre-check username and email uniqueness
    username = request.data.get('username')
    email = request.data.get('email')
    if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
        return Response({
            "success": False,
            "message": "Username or email is already taken.",
            "error_code": "USER_ALREADY_EXISTS"
        }, status=status.HTTP_409_CONFLICT)

    # Validate and save
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        # Enhancement: generate token immediately after successful registration
        refresh = RefreshToken.for_user(user)
        token = str(refresh.access_token)
        return Response({
            "success": True,
            "message": "User registered successfully",
            "data": {
                "token": token,
                "user": {
                    "userid": user.id,
                    "username": user.username,
                    "email": user.email,
                    "createdAt": user.date_joined.replace(microsecond=0).isoformat() + 'Z',
                }
            }
        }, status=status.HTTP_201_CREATED)
    else:
        errors = serializer.errors
        error_code = "VALIDATION_FAILED"
        return Response({
            "success": False,
            "message": "Request validation failed. Please check the submitted data.",
            "error_code": error_code,
            "errors": errors
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login(request):
    serializer = LoginSerializer(data=request.data)
    # 400 If validation fails, return 400
    if not serializer.is_valid():
        return Response({
            "success": False,
            "message": "Request validation failed. Please check the submitted data.",
            "error_code": "VALIDATION_FAILED",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    #validate the data
    username = serializer.validated_data['username']
    password = serializer.validated_data['password']
    #validate the authentication
    user = authenticate(username=username, password=password)
    if user is None:
        return Response({
            "success": False,
            "message": "Invalid username or password.",
            "error_code": "INVALID_CREDENTIALS"
        }, status=status.HTTP_401_UNAUTHORIZED)

          # Issue a token to the user
    try:
        refresh = RefreshToken.for_user(user) # Create a refresh token for the user
        token = str(refresh.access_token)  # Return the access token as a string
    except Exception:
        token = None

    # Check if the user is a member
    is_Member = user.groups.filter(name="Member").exists()
     # Success!!
    return Response({
        "success": True,
        "message": "Login successful",
        "data": {
            "token": token,
            "user": {
                "userid": user.id,
                "username": user.username,
                "email": user.email,
                "isMember": is_Member,
            }
        }
    }, status=status.HTTP_200_OK)


