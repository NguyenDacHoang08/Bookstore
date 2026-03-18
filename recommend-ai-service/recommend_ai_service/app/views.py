from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
import math
from .models import BookRating, UserInteraction
from .serializers import BookRatingSerializer, UserInteractionSerializer

class Health(APIView):
    def get(self, request):
        return Response({
            "service": "recommend-ai-service",
            "status": "ok",
        })

class AddRating(APIView):
    def post(self, request):
        serializer = BookRatingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AddInteraction(APIView):
    def post(self, request):
        serializer = UserInteractionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def cosine_similarity(vec1, vec2):
    dot = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))
    if norm1 == 0 or norm2 == 0:
        return 0
    return dot / (norm1 * norm2)

def get_collaborative_recommendations(user_id, book_id, n_recommendations=5):
    # Fetch all ratings
    ratings = list(BookRating.objects.all().values('user_id', 'book_id', 'rating'))
    if not ratings:
        return []
    
    # Get unique users and books
    users = list(set(r['user_id'] for r in ratings))
    books = list(set(r['book_id'] for r in ratings))
    
    if user_id not in users:
        return []
    
    # Create rating dict
    user_ratings = {}
    for r in ratings:
        uid = r['user_id']
        bid = r['book_id']
        if uid not in user_ratings:
            user_ratings[uid] = {}
        user_ratings[uid][bid] = r['rating']
    
    # Get current user's ratings
    current_ratings = user_ratings.get(user_id, {})
    
    # Compute similarities
    similarities = []
    for other_user in users:
        if other_user == user_id:
            continue
        other_ratings = user_ratings.get(other_user, {})
        
        # Common books
        common = set(current_ratings.keys()) & set(other_ratings.keys())
        if not common:
            continue
        
        vec1 = [current_ratings[b] for b in common]
        vec2 = [other_ratings[b] for b in common]
        sim = cosine_similarity(vec1, vec2)
        similarities.append((other_user, sim))
    
    # Sort by similarity descending
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    # Get recommendations
    user_rated_books = set(current_ratings.keys())
    recommendations = []
    for sim_user, _ in similarities[:5]:  # Top 5
        for bid, rating in user_ratings.get(sim_user, {}).items():
            if bid not in user_rated_books and rating >= 4:
                recommendations.append(bid)
    
    # Remove duplicates and current book
    recommendations = list(set(recommendations) - {book_id})
    
    return recommendations[:n_recommendations]

class RecommendBooks(APIView):
    def get(self, request, book_id):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({"error": "user_id required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user_id = int(user_id)
        except ValueError:
            return Response({"error": "Invalid user_id"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Try AI recommendations first
        ai_recommendations = get_collaborative_recommendations(user_id, book_id)
        if ai_recommendations:
            # Fetch book details from book-service
            recommendations = []
            for rec_book_id in ai_recommendations:
                try:
                    book_response = requests.get(f'http://book-service:8000/books/{rec_book_id}/')
                    if book_response.status_code == 200:
                        recommendations.append(book_response.json())
                except:
                    pass
            return Response(recommendations)
        
        # Fallback to simple logic
        try:
            # Call book-service to get the current book
            book_response = requests.get(f'http://book-service:8000/books/{book_id}/')
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
                    key=lambda x: x.get('rating_avg', 0), reverse=True
                )[:5 - len(recommendations)]
                recommendations.extend(high_rated)
            
            return Response(recommendations[:5])  # Return top 5
            
        except requests.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
