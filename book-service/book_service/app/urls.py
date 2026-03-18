from django.urls import path
from .views import BookListCreate, BookDetail, BookRate, BookStockAdjust
urlpatterns = [
    path('books/', BookListCreate.as_view()),
    path('books/<int:book_id>/', BookDetail.as_view()),
    path('books/<int:book_id>/rate/', BookRate.as_view()),
    path('books/<int:book_id>/stock/', BookStockAdjust.as_view()),
]
