from django.shortcuts import get_object_or_404
from django.db.models import F
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Book
from .serializers import BookSerializer

class BookListCreate(APIView):
    def get(self, request):
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)
    def post(self, request):
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BookDetail(APIView):
    def get(self, request, book_id):
        book = get_object_or_404(Book, id=book_id)
        serializer = BookSerializer(book)
        return Response(serializer.data)

    def put(self, request, book_id):
        book = get_object_or_404(Book, id=book_id)
        serializer = BookSerializer(book, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, book_id):
        book = get_object_or_404(Book, id=book_id)
        serializer = BookSerializer(book, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, book_id):
        book = get_object_or_404(Book, id=book_id)
        book.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BookRate(APIView):
    def post(self, request, book_id):
        book = get_object_or_404(Book, id=book_id)
        try:
            rating = int(request.data.get("rating"))
        except (TypeError, ValueError):
            return Response(
                {"error": "rating must be an integer"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if rating < 1 or rating > 5:
            return Response(
                {"error": "rating must be between 1 and 5"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        new_count = book.rating_count + 1
        new_avg = ((book.rating_avg * book.rating_count) + rating) / new_count
        book.rating_avg = new_avg
        book.rating_count = new_count
        book.save(update_fields=["rating_avg", "rating_count"])

        serializer = BookSerializer(book)
        return Response(serializer.data)


class BookStockAdjust(APIView):
    def post(self, request, book_id):
        try:
            delta = int(request.data.get("delta"))
        except (TypeError, ValueError):
            return Response(
                {"error": "delta must be an integer"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if delta == 0:
            return Response(
                {"error": "delta must be non-zero"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        book = Book.objects.filter(id=book_id).first()
        if not book:
            return Response(
                {"error": "Book not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if delta < 0:
            quantity = abs(delta)
            updated = Book.objects.filter(id=book_id, stock__gte=quantity).update(
                stock=F("stock") - quantity
            )
            if updated == 0:
                return Response(
                    {"error": "insufficient stock"},
                    status=status.HTTP_409_CONFLICT,
                )
        else:
            Book.objects.filter(id=book_id).update(stock=F("stock") + delta)

        book.refresh_from_db()
        serializer = BookSerializer(book)
        return Response(serializer.data, status=status.HTTP_200_OK)
