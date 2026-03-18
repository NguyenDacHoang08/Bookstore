from django.urls import path
from .views import Health, PaymentListCreate

urlpatterns = [
    path('health/', Health.as_view()),
    path('payments/', PaymentListCreate.as_view()),
]
