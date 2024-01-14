import random

from django.conf import settings
from datetime import datetime, timedelta
import jwt
from django.core.mail import send_mail
from django.utils.html import strip_tags
from django.template.loader import render_to_string

from members.models import User


def generate_access_token(user):
	payload = {
		'user_id': user.user_id,
		'exp': datetime.utcnow() + timedelta(days=0, minutes=30),
		'iat': datetime.utcnow(),
	}

	access_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
	return access_token


def send_email_to_user(email, subject, plain_message):
	from_email = settings.EMAIL_HOST_USER
	send_mail(subject, plain_message, from_email, (email,))

def send_otp(email,subject):
	from_email = settings.EMAIL_HOST_USER
	otp = random.randint(1000,9999)
	send_mail(subject, str(otp), from_email, (email,))
	return otp

