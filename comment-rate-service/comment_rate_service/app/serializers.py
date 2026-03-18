from rest_framework import serializers
from .models import Rating


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = [
            "id",
            "customer_id",
            "book_id",
            "rating",
            "comment",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
