from django.urls import path
from .views import Health, OrderListCreate, OrderDetail, OrderApprove

urlpatterns = [
    path('health/', Health.as_view()),
    path('orders/', OrderListCreate.as_view()),
    path('orders/<int:order_id>/', OrderDetail.as_view()),
    path('orders/<int:order_id>/approve/', OrderApprove.as_view()),
]
