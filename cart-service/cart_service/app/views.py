from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
import requests

BOOK_SERVICE_URL = "http://book-service:8000"

class CartCreate(APIView):
    def post(self, request):
        serializer = CartSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddCartItem(APIView):
    def post(self, request):
        customer_id = request.data.get("customer_id")
        cart_id = request.data.get("cart")
        try:
            book_id = int(request.data.get("book_id"))
            quantity = int(request.data.get("quantity", 1))
        except (TypeError, ValueError):
            return Response(
                {"error": "book_id and quantity are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not customer_id and not cart_id:
            return Response(
                {"error": "customer_id or cart is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if quantity <= 0:
            return Response(
                {"error": "quantity must be greater than 0"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            book_response = requests.get(
                f"{BOOK_SERVICE_URL}/books/{book_id}/",
                timeout=3,
            )
        except requests.RequestException:
            return Response(
                {"error": "book-service unavailable"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        if book_response.status_code == 404:
            return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)
        if book_response.status_code != 200:
            return Response(
                {"error": "book-service unavailable"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        cart = None
        if cart_id:
            cart = Cart.objects.filter(id=cart_id).first()
        if not cart:
            try:
                customer_id = int(customer_id)
            except (TypeError, ValueError):
                return Response(
                    {"error": "customer_id must be an integer"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            cart, _ = Cart.objects.get_or_create(customer_id=customer_id)
        item, created = CartItem.objects.get_or_create(
            cart=cart,
            book_id=book_id,
            defaults={"quantity": quantity},
        )

        if not created:
            item.quantity += quantity
            item.save(update_fields=["quantity"])

        serializer = CartItemSerializer(item)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ViewCart(APIView):
    def get(self, request, customer_id):
        cart = Cart.objects.filter(customer_id=customer_id).first()
        if not cart:
            return Response([])
        items = CartItem.objects.filter(cart=cart).order_by("id")
        serializer = CartItemSerializer(items, many=True)
        return Response(serializer.data)

    def delete(self, request, customer_id):
        cart = Cart.objects.filter(customer_id=customer_id).first()
        if not cart:
            return Response(status=status.HTTP_204_NO_CONTENT)
        cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CartItemDetail(APIView):
    def patch(self, request, item_id):
        try:
            quantity = int(request.data.get("quantity"))
        except (TypeError, ValueError):
            return Response(
                {"error": "quantity is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        item = CartItem.objects.filter(id=item_id).first()
        if not item:
            return Response({"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND)

        if quantity <= 0:
            item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        item.quantity = quantity
        item.save(update_fields=["quantity"])
        serializer = CartItemSerializer(item)
        return Response(serializer.data)

    def delete(self, request, item_id):
        item = CartItem.objects.filter(id=item_id).first()
        if not item:
            return Response({"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
