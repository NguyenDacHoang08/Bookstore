from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import check_password
from .models import Customer
from .serializers import CustomerSerializer
import requests

CART_SERVICE_URL = "http://cart-service:8000"

class CustomerListCreate(APIView):
    def get(self, request):
        customers = Customer.objects.all()
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            customer = serializer.save()
            # Call cart-service
            requests.post(
            f"{CART_SERVICE_URL}/carts/",
                json={"customer_id": customer.id}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerLoginView(APIView):
    def post(self, request):
        email = request.data.get('email', '').strip()
        password = request.data.get('password', '').strip()
        
        if not email or not password:
            return Response(
                {'error': 'Email and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            customer = Customer.objects.get(email=email)
        except Customer.DoesNotExist:
            return Response(
                {'error': 'Customer not found'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if not check_password(password, customer.password):
            return Response(
                {'error': 'Invalid password'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Generate JWT tokens
        refresh = RefreshToken()
        refresh['email'] = customer.email
        refresh['customer_id'] = customer.id
        refresh['user_type'] = 'customer'
        refresh['name'] = customer.name
        
        return Response({
            'id': customer.id,
            'email': customer.email,
            'name': customer.name,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user_type': 'customer'
        }, status=status.HTTP_200_OK)