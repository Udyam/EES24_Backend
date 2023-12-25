from django.conf import settings
from datetime import datetime, timedelta
import jwt


def generate_access_token(user):
	payload = {
		'user_id': user.user_id,
		'exp': datetime.utcnow() + timedelta(days=0, minutes=30),
		'iat': datetime.utcnow(),
	}

	access_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
	return access_token