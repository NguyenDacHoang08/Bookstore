from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Order, OrderItem
from .serializers import OrderSerializer
import requests

PAY_SERVICE_URL = "http://pay-service:8000"
SHIP_SERVICE_URL = "http://ship-service:8000"
CART_SERVICE_URL = "http://cart-service:8000"
BOOK_SERVICE_URL = "http://book-service:8000"

MONEY_PLACES = Decimal("0.01")


class Health(APIView):
    def get(self, request):
        return Response({
            "service": "order-service",
            "status": "ok",
        })


def _quantize_amount(value):
    return value.quantize(MONEY_PLACES, rounding=ROUND_HALF_UP)


def _fetch_cart_items(customer_id):
    try:
        cart_response = requests.get(
            f"{CART_SERVICE_URL}/carts/{customer_id}/",
            timeout=3,
        )
    except requests.RequestException:
        return None, {"error": "cart-service unavailable"}, status.HTTP_503_SERVICE_UNAVAILABLE

    if cart_response.status_code != status.HTTP_200_OK:
        return None, {"error": "cart-service unavailable"}, status.HTTP_503_SERVICE_UNAVAILABLE

    try:
        cart_items = cart_response.json()
    except ValueError:
        return None, {"error": "cart-service invalid response"}, status.HTTP_502_BAD_GATEWAY

    if not cart_items:
        return None, {"error": "cart is empty"}, status.HTTP_400_BAD_REQUEST

    return cart_items, None, None


def _build_order_items(cart_items):
    items = []
    total = Decimal("0.00")

    for item in cart_items:
        book_id = item.get("book_id")
        quantity = item.get("quantity")
        try:
            book_id = int(book_id)
            quantity = int(quantity)
        except (TypeError, ValueError):
            return None, None, {"error": "invalid cart item"}, status.HTTP_400_BAD_REQUEST

        if quantity <= 0:
            return None, None, {"error": "invalid cart item quantity"}, status.HTTP_400_BAD_REQUEST

        try:
            book_response = requests.get(
                f"{BOOK_SERVICE_URL}/books/{book_id}/",
                timeout=3,
            )
        except requests.RequestException:
            return None, None, {"error": "book-service unavailable"}, status.HTTP_503_SERVICE_UNAVAILABLE

        if book_response.status_code == status.HTTP_404_NOT_FOUND:
            return None, None, {"error": "Book not found"}, status.HTTP_404_NOT_FOUND
        if book_response.status_code != status.HTTP_200_OK:
            return None, None, {"error": "book-service unavailable"}, status.HTTP_503_SERVICE_UNAVAILABLE

        try:
            book_data = book_response.json()
        except ValueError:
            return None, None, {"error": "book-service invalid response"}, status.HTTP_502_BAD_GATEWAY

        try:
            unit_price = Decimal(str(book_data.get("price")))
        except (TypeError, InvalidOperation):
            return None, None, {"error": "invalid book price"}, status.HTTP_502_BAD_GATEWAY

        try:
            stock = int(book_data.get("stock"))
        except (TypeError, ValueError):
            return None, None, {"error": "invalid book stock"}, status.HTTP_502_BAD_GATEWAY

        if stock < quantity:
            return None, None, {"error": "insufficient stock"}, status.HTTP_409_CONFLICT

        unit_price = _quantize_amount(unit_price)
        line_total = _quantize_amount(unit_price * quantity)
        total = _quantize_amount(total + line_total)

        items.append({
            "book_id": book_id,
            "title": book_data.get("title") or "",
            "author": book_data.get("author") or "",
            "unit_price": unit_price,
            "quantity": quantity,
            "line_total": line_total,
        })

    return total, items, None, None


def _adjust_book_stock(book_id, delta):
    try:
        response = requests.post(
            f"{BOOK_SERVICE_URL}/books/{book_id}/stock/",
            json={"delta": delta},
            timeout=3,
        )
    except requests.RequestException:
        return {"error": "book-service unavailable"}, status.HTTP_503_SERVICE_UNAVAILABLE

    if response.status_code == status.HTTP_404_NOT_FOUND:
        return {"error": "Book not found"}, status.HTTP_404_NOT_FOUND
    if response.status_code == status.HTTP_409_CONFLICT:
        return {"error": "insufficient stock"}, status.HTTP_409_CONFLICT
    if response.status_code != status.HTTP_200_OK:
        return {"error": "book-service unavailable"}, status.HTTP_503_SERVICE_UNAVAILABLE

    return None, None


def _reserve_stock(items):
    reserved = []
    for item in items:
        error_body, error_status = _adjust_book_stock(item["book_id"], -item["quantity"])
        if error_body:
            _restore_stock(reserved)
            return error_body, error_status
        reserved.append(item)
    return None, None


def _restore_stock(items):
    for item in items:
        _adjust_book_stock(item["book_id"], item["quantity"])


class OrderListCreate(APIView):
    def get(self, request):
        orders = Order.objects.all().order_by("-created_at").prefetch_related("items")
        customer_id = request.query_params.get("customer_id")
        if customer_id:
            try:
                customer_id = int(customer_id)
            except (TypeError, ValueError):
                return Response(
                    {"error": "customer_id must be an integer"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            orders = orders.filter(customer_id=customer_id)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    def post(self, request):
        customer_id = request.data.get("customer_id")
        payment_method = request.data.get("payment_method")
        shipping_method = request.data.get("shipping_method")
        shipping_address = request.data.get("shipping_address", "")
        amount_raw = request.data.get("total_amount")

        try:
            customer_id = int(customer_id)
        except (TypeError, ValueError):
            return Response(
                {"error": "customer_id must be an integer"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not payment_method:
            return Response(
                {"error": "payment_method is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not shipping_method:
            return Response(
                {"error": "shipping_method is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cart_items, error_body, error_status = _fetch_cart_items(customer_id)
        if error_body:
            return Response(error_body, status=error_status)

        total_amount, items_data, error_body, error_status = _build_order_items(cart_items)
        if error_body:
            return Response(error_body, status=error_status)

        if amount_raw is not None and str(amount_raw).strip() != "":
            try:
                provided_amount = Decimal(str(amount_raw))
            except (TypeError, InvalidOperation):
                return Response(
                    {"error": "total_amount must be a number"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if provided_amount < 0:
                return Response(
                    {"error": "total_amount must be >= 0"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            provided_amount = _quantize_amount(provided_amount)
            if provided_amount != total_amount:
                return Response(
                    {
                        "error": "total_amount does not match cart total",
                        "expected_total": str(total_amount),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        reserve_error_body, reserve_error_status = _reserve_stock(items_data)
        if reserve_error_body:
            return Response(reserve_error_body, status=reserve_error_status)

        try:
            with transaction.atomic():
                order = Order.objects.create(
                    customer_id=customer_id,
                    total_amount=total_amount,
                    payment_method=payment_method,
                    shipping_method=shipping_method,
                    shipping_address=shipping_address,
                    status="processing",
                )
                OrderItem.objects.bulk_create(
                    [
                        OrderItem(
                            order=order,
                            book_id=item["book_id"],
                            title=item["title"],
                            author=item["author"],
                            unit_price=item["unit_price"],
                            quantity=item["quantity"],
                            line_total=item["line_total"],
                        )
                        for item in items_data
                    ]
                )
        except Exception:
            _restore_stock(items_data)
            return Response(
                {"error": "failed to create order"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        payment_payload = {
            "order_id": order.id,
            "amount": str(order.total_amount),
            "method": payment_method,
        }
        try:
            payment_response = requests.post(
                f"{PAY_SERVICE_URL}/payments/",
                json=payment_payload,
                timeout=3,
            )
        except requests.RequestException:
            _restore_stock(items_data)
            order.payment_status = "failed"
            order.status = "failed"
            order.save(update_fields=["payment_status", "status"])
            return Response(
                {"error": "pay-service unavailable", "order": OrderSerializer(order).data},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        if payment_response.status_code != status.HTTP_201_CREATED:
            _restore_stock(items_data)
            order.payment_status = "failed"
            order.status = "failed"
            order.save(update_fields=["payment_status", "status"])
            return Response(
                {"error": "payment failed", "order": OrderSerializer(order).data},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        try:
            payment_data = payment_response.json()
        except ValueError:
            payment_data = {}

        order.payment_status = payment_data.get("status", "paid")
        order.payment_id = payment_data.get("id")
        order.save(update_fields=["payment_status", "payment_id"])

        shipment_payload = {
            "order_id": order.id,
            "method": shipping_method,
            "address": shipping_address,
        }
        try:
            shipment_response = requests.post(
                f"{SHIP_SERVICE_URL}/shipments/",
                json=shipment_payload,
                timeout=3,
            )
        except requests.RequestException:
            order.shipping_status = "failed"
            order.status = "failed"
            order.save(update_fields=["shipping_status", "status"])
            return Response(
                {"error": "ship-service unavailable", "order": OrderSerializer(order).data},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        if shipment_response.status_code != status.HTTP_201_CREATED:
            order.shipping_status = "failed"
            order.status = "failed"
            order.save(update_fields=["shipping_status", "status"])
            return Response(
                {"error": "shipping failed", "order": OrderSerializer(order).data},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        try:
            shipment_data = shipment_response.json()
        except ValueError:
            shipment_data = {}

        order.shipping_status = shipment_data.get("status", "created")
        order.shipment_id = shipment_data.get("id")
        order.status = "confirmed"
        order.save(update_fields=["shipping_status", "shipment_id", "status"])

        try:
            requests.delete(
                f"{CART_SERVICE_URL}/carts/{customer_id}/",
                timeout=3,
            )
        except requests.RequestException:
            pass

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class OrderDetail(APIView):
    def get(self, request, order_id):
        order = Order.objects.filter(id=order_id).prefetch_related("items").first()
        if not order:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = OrderSerializer(order)
        return Response(serializer.data)
