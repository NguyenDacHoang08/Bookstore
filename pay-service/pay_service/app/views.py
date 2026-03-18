from decimal import Decimal, InvalidOperation
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Payment
from .serializers import PaymentSerializer


class Health(APIView):
    def get(self, request):
        return Response({
            "service": "pay-service",
            "status": "ok",
        })


class PaymentListCreate(APIView):
    def get(self, request):
        payments = Payment.objects.all().order_by("-created_at")
        order_id = request.query_params.get("order_id")
        if order_id:
            try:
                order_id = int(order_id)
            except (TypeError, ValueError):
                return Response(
                    {"error": "order_id must be an integer"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            payments = payments.filter(order_id=order_id)
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)

    def post(self, request):
        order_id = request.data.get("order_id")
        method = request.data.get("method")
        amount_raw = request.data.get("amount")

        try:
            order_id = int(order_id)
        except (TypeError, ValueError):
            return Response(
                {"error": "order_id must be an integer"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not method:
            return Response(
                {"error": "method is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            amount = Decimal(str(amount_raw))
        except (TypeError, InvalidOperation):
            return Response(
                {"error": "amount must be a number"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if amount < 0:
            return Response(
                {"error": "amount must be >= 0"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payment = Payment.objects.create(
            order_id=order_id,
            amount=amount,
            method=method,
            status="paid",
        )
        serializer = PaymentSerializer(payment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
