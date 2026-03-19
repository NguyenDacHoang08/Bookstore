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
            "approval_status",
            "approved_by",
            "approved_at",
            "rejection_reason",
            "tracking_number",
            "estimated_delivery",
            "notes",
            "created_at",
            "updated_at",
            "items",
        ]
        read_only_fields = [
            "id",
            "payment_status",
            "shipping_status",
            "status",
            "payment_id",
            "shipment_id",
            "approval_status",
            "approved_by",
            "approved_at",
            "created_at",
            "updated_at",
            "items",
        ]


class OrderTrackingSerializer(serializers.ModelSerializer):
    """Serializer cho customer theo dõi đơn hàng"""
    items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = [
            "id",
            "total_amount",
            "payment_method",
            "shipping_method",
            "payment_status",
            "shipping_status",
            "status",
            "shipping_address",
            "approval_status",
            "tracking_number",
            "estimated_delivery",
            "created_at",
            "updated_at",
            "items",
        ]


class OrderApprovalSerializer(serializers.ModelSerializer):
    """Serializer cho staff duyệt đơn hàng"""
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
            "shipping_address",
            "approval_status",
            "approved_by",
            "approved_at",
            "rejection_reason",
            "tracking_number",
            "estimated_delivery",
            "notes",
            "created_at",
            "updated_at",
            "items",
        ]


class ApprovalActionSerializer(serializers.Serializer):
    """Serializer cho hành động duyệt/từ chối đơn hàng"""
    action = serializers.ChoiceField(choices=['approve', 'reject'])
    staff_id = serializers.IntegerField()
    rejection_reason = serializers.CharField(required=False, allow_blank=True)
    tracking_number = serializers.CharField(required=False, allow_blank=True)
    estimated_delivery = serializers.DateTimeField(required=False)
    notes = serializers.CharField(required=False, allow_blank=True)
