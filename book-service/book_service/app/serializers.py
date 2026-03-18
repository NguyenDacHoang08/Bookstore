from rest_framework import serializers
from .models import Book
class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = (
            'id',
            'title',
            'author',
            'price',
            'stock',
            'rating_avg',
            'rating_count',
        )
        read_only_fields = ('rating_avg', 'rating_count')
