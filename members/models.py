from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from ckeditor_uploader.fields import RichTextUploadingField
import hashlib
import secrets


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('A user email is needed.')

        if not password:
            raise ValueError('A user password is needed.')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('A user email is needed.')

        if not password:
            raise ValueError('A user password is needed.')

        user = self.create_user(email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=100, unique=True)
    name = models.CharField(max_length=100, unique=True)
    otp = models.CharField(max_length=64, default='', blank=True)
    college = models.CharField(max_length=100)
    year = models.IntegerField()
    is_verified = models.BooleanField(default=False)
    password_confirmation = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateField(auto_now_add=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def set_and_hash_otp(self, otp):
        # Hash the OTP directly without using a salt
        hashed_otp = hashlib.sha256(str(otp).encode()).hexdigest()

        # Save the hashed OTP to the model
        self.otp = hashed_otp
        self.save()

    def check_otp(self, entered_otp):
        if not self.otp:
            return False

        # Hash the entered OTP
        entered_otp_str = str(entered_otp)
        hashed_entered_otp = hashlib.sha256(entered_otp_str.encode()).hexdigest()

        # Compare the stored hashed OTP with the newly hashed entered OTP
        return self.otp == hashed_entered_otp

    def __str__(self):
        return self.email


class BroadCast_Email(models.Model):
    subject = models.CharField(max_length=200)
    created = models.DateTimeField(default=timezone.now)
    message = RichTextUploadingField()

    def __unicode__(self):
        return self.subject

    class Meta:
        verbose_name = "BroadCast Email to all Member"
        verbose_name_plural = "BroadCast Email"


class UserQueries(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    AskedWhen = models.DateTimeField(auto_now_add=True)
    question = models.TextField(max_length=200)

    def __str__(self):
        return self.email
