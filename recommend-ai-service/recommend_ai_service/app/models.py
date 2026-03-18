from django.db import models
from django.contrib.auth.models import User

class BookRating(models.Model):
    user_id = models.IntegerField()  # Since users might be in another service
    book_id = models.IntegerField()
    rating = models.FloatField()  # 1-5 stars
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user_id', 'book_id')

class UserInteraction(models.Model):
    user_id = models.IntegerField()
    book_id = models.IntegerField()
    interaction_type = models.CharField(max_length=20)  # 'view', 'purchase', 'add_to_cart'
    created_at = models.DateTimeField(auto_now_add=True)