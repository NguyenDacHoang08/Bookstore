from django.urls import path
from .views import Health, OrderListCreate, OrderDetail

urlpatterns = [
    path('health/', Health.as_view()),
    path('orders/', OrderListCreate.as_view()),
    path('orders/<int:order_id>/', OrderDetail.as_view()),
]
