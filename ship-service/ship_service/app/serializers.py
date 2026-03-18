from rest_framework import serializers
from .models import Shipment


class ShipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipment
        fields = [
            "id",
            "order_id",
            "method",
            "address",
            "status",
            "created_at",
        ]
        read_only_fields = ["id", "status", "created_at"]
