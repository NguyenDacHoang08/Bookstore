"""ASGI config for recommend_ai_service project."""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recommend_ai_service.settings')

application = get_asgi_application()
