from django.urls import path
from .views import (
    Health, OrderListCreate, OrderDetail, 
    OrderTracking, OrderApproval, PendingOrdersList
)

urlpatterns = [
    path('health/', Health.as_view()),
    path('orders/', OrderListCreate.as_view()),
    path('orders/<int:order_id>/', OrderDetail.as_view()),
    
    # Endpoint cho customer theo dõi đơn hàng
    path('orders/<int:order_id>/tracking/', OrderTracking.as_view()),
    path('customers/<int:customer_id>/orders/', OrderTracking.as_view()),
    
    # Endpoint cho staff duyệt đơn hàng
    path('orders/<int:order_id>/approval/', OrderApproval.as_view()),
    path('orders/pending/', PendingOrdersList.as_view()),
]
