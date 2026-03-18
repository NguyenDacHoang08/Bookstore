from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Shipment
from .serializers import ShipmentSerializer


class Health(APIView):
    def get(self, request):
        return Response({
            "service": "ship-service",
            "status": "ok",
        })


class ShipmentListCreate(APIView):
    def get(self, request):
        shipments = Shipment.objects.all().order_by("-created_at")
        order_id = request.query_params.get("order_id")
        if order_id:
            try:
                order_id = int(order_id)
            except (TypeError, ValueError):
                return Response(
                    {"error": "order_id must be an integer"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            shipments = shipments.filter(order_id=order_id)
        serializer = ShipmentSerializer(shipments, many=True)
        return Response(serializer.data)

    def post(self, request):
        order_id = request.data.get("order_id")
        method = request.data.get("method")
        address = request.data.get("address", "")

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

        shipment = Shipment.objects.create(
            order_id=order_id,
            method=method,
            address=address,
            status="created",
        )
        serializer = ShipmentSerializer(shipment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
