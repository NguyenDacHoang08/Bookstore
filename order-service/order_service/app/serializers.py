from rest_framework import serializers
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = [
            "id",
            "book_id",
            "title",
            "author",
            "unit_price",
            "quantity",
            "line_total",
        ]
        read_only_fields = ["id"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "customer_id",
            "total_amount",
            "payment_method",
            "shipping_method",
            "payment_status",
            "shipping_status",
            "status",
            "payment_id",
            "shipment_id",
            "shipping_address",
            "created_at",
            "items",
        ]
        read_only_fields = [
            "id",
            "payment_status",
            "shipping_status",
            "status",
            "payment_id",
            "shipment_id",
            "created_at",
            "items",
        ]
