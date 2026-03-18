from django.urls import path
from .views import Health, RecommendBooks

urlpatterns = [
    path('health/', Health.as_view()),
    path('recommend/<int:book_id>/', RecommendBooks.as_view()),
]
