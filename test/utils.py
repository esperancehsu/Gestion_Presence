# tests/utils.py
import jwt
from datetime import datetime, timedelta
from django.conf import settings

def generate_jwt_token(user_id):
    payload = {
        "id": user_id,
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow(),
        "type": "access"
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")