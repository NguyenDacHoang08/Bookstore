from django.urls import path
from .views import Health, RatingList, BookRate

urlpatterns = [
    path('health/', Health.as_view()),
    path('ratings/', RatingList.as_view()),
    path('books/<int:book_id>/rate/', BookRate.as_view()),
]
