from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Rating
from .serializers import RatingSerializer
from django.db import IntegrityError
import requests

BOOK_SERVICE_URL = "http://book-service:8000"


class Health(APIView):
    def get(self, request):
        return Response({
            "service": "comment-rate-service",
            "status": "ok",
        })


class RatingList(APIView):
    def get(self, request):
        ratings = Rating.objects.all().order_by("-created_at")
        book_id = request.query_params.get("book_id")
        if book_id:
            try:
                book_id = int(book_id)
            except (TypeError, ValueError):
                return Response(
                    {"error": "book_id must be an integer"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            ratings = ratings.filter(book_id=book_id)
        serializer = RatingSerializer(ratings, many=True)
        return Response(serializer.data)


class BookRate(APIView):
    def post(self, request, book_id):
        try:
            rating_value = int(request.data.get("rating"))
        except (TypeError, ValueError):
            return Response(
                {"error": "rating must be an integer"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if rating_value < 1 or rating_value > 5:
            return Response(
                {"error": "rating must be between 1 and 5"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        customer_id = request.data.get("customer_id")
        if customer_id is not None:
            try:
                customer_id = int(customer_id)
            except (TypeError, ValueError):
                return Response(
                    {"error": "customer_id must be an integer"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        comment = request.data.get("comment", "")

        try:
            book_response = requests.post(
                f"{BOOK_SERVICE_URL}/books/{book_id}/rate/",
                json={"rating": rating_value},
                timeout=3,
            )
        except requests.RequestException:
            return Response(
                {"error": "book-service unavailable"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        if book_response.status_code == status.HTTP_404_NOT_FOUND:
            return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)
        if book_response.status_code != status.HTTP_200_OK:
            return Response(
                {"error": "book-service unavailable"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        try:
            rating = Rating.objects.create(
                customer_id=customer_id,
                book_id=book_id,
                rating=rating_value,
                comment=comment,
            )
        except IntegrityError:
            return Response(
                {"error": "You have already rated this book"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = RatingSerializer(rating)

        try:
            book_data = book_response.json()
        except ValueError:
            book_data = None

        return Response(
            {
                "book": book_data,
                "rating": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
