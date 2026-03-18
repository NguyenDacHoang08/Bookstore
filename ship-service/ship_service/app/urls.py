from django.urls import path
from .views import Health, ShipmentListCreate

urlpatterns = [
    path('health/', Health.as_view()),
    path('shipments/', ShipmentListCreate.as_view()),
]
