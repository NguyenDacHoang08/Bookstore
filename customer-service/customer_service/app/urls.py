from django.urls import path
from .views import CustomerListCreate, CustomerLoginView

urlpatterns = [
    path('customers/', CustomerListCreate.as_view()),
    path('login/', CustomerLoginView.as_view()),
]