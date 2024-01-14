from rest_framework.response import Response
from rest_framework import serializers, status
from django.contrib.auth import get_user_model
from .models import *


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'phone_number','username', 'password','password_confirmation']

    def create(self, validated_data):
        user_password = validated_data.get('password', None)
        db_instance = self.Meta.model(email=validated_data.get('email'), username=validated_data.get('username'),
                                      phone_number=validated_data.get('phone_number'))
        db_instance.set_password(user_password)
        db_instance.save()
        return db_instance


class UserLoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=100)
    username = serializers.CharField(max_length=100, read_only=True)
    password = serializers.CharField(max_length=100, min_length=8, style={'input_type': 'password'})
    token = serializers.CharField(max_length=255, read_only=True)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'username']


class BroadCastSerializer(serializers.Serializer):
    subject = serializers.CharField(max_length=50)
    message = serializers.CharField(max_length=500)


class VerifyAccountSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=100)
    otp = serializers.IntegerField()

class EmailSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=100)

class OtpPasswordSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=100)
    otp = serializers.IntegerField()
    password1 = serializers.CharField(max_length=100)
    password2 = serializers.CharField(max_length=100)




