from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests


class Health(APIView):
    def get(self, request):
        return Response({
            "service": "recommend-ai-service",
            "status": "ok",
        })


class RecommendBooks(APIView):
    def get(self, request, book_id):
        try:
            # Call book-service to get the current book
            book_response = requests.get('http://book-service:8000/books/{book_id}/')
            if book_response.status_code != 200:
                return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)
            current_book = book_response.json()
            
            # Get all books
            books_response = requests.get('http://book-service:8000/books/')
            if books_response.status_code != 200:
                return Response({"error": "Unable to fetch books"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            all_books = books_response.json()
            
            # Simple recommendation: books by same author, excluding current book
            recommendations = [
                book for book in all_books 
                if book['author'] == current_book['author'] and book['id'] != book_id
            ]
            
            # If not enough, add high-rated books
            if len(recommendations) < 5:
                high_rated = sorted(
                    [book for book in all_books if book['id'] != book_id and book not in recommendations],
                    key=lambda x: x['rating_avg'], reverse=True
                )[:5 - len(recommendations)]
                recommendations.extend(high_rated)
            
            return Response(recommendations[:5])  # Return top 5
            
        except requests.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
