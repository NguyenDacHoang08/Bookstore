from django.contrib import admin
from .models import BookRating, UserInteraction

@admin.register(BookRating)
class BookRatingAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'book_id', 'rating', 'created_at')

@admin.register(UserInteraction)
class UserInteractionAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'book_id', 'interaction_type', 'created_at')