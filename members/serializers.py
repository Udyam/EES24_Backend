from rest_framework.response import Response
from rest_framework import serializers, status
from django.contrib.auth import get_user_model
from .models import *


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'name', 'college', 'year', 'password', 'password_confirmation']

    def create(self, validated_data):
        user_password = validated_data.get('password', None)
        db_instance = self.Meta.model(email=validated_data.get('email'), name=validated_data.get('name'),
                                       college=validated_data.get('college'), year=validated_data.get('year'))
        db_instance.set_password(user_password)
        db_instance.save()
        return db_instance


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'})


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'name', 'college', 'year']


class BroadCastSerializer(serializers.Serializer):
    subject = serializers.CharField(max_length=50)
    message = serializers.CharField(max_length=100)


class VerifyAccountSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=4)


class EmailSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=100)


class OtpPasswordSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=100)
    otp = serializers.IntegerField()
    password1 = serializers.CharField(max_length=100)
    password2 = serializers.CharField(max_length=100)


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['college', 'name', 'year']

class UserQuerySerializer(serializers.ModelSerializer):

    class Meta:
        model = UserQueries
        fields = ['name','email','question']