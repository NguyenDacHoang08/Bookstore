from django.urls import path
from .views import Health, StaffListCreate, StaffBookListCreate, StaffBookDetail

urlpatterns = [
    path('health/', Health.as_view()),
    path('staffs/', StaffListCreate.as_view()),
    path('books/', StaffBookListCreate.as_view()),
    path('books/<int:book_id>/', StaffBookDetail.as_view()),
]
