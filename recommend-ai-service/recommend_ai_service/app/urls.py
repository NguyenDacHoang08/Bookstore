from django.urls import path
from .views import Health, RecommendBooks, AddRating, AddInteraction

urlpatterns = [
    path('health/', Health.as_view()),
    path('recommend/<int:book_id>/', RecommendBooks.as_view()),
    path('rating/', AddRating.as_view()),
    path('interaction/', AddInteraction.as_view()),
]
