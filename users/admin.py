from django.contrib import admin

# api/admin.py (suite)
from .models import User

admin.site.register(User)
