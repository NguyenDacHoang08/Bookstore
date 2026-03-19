from decimal import Decimal, InvalidOperation
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
import requests

BOOK_SERVICE_URL = "http://book-service:8000"
CART_SERVICE_URL = "http://cart-service:8000"
COMMENT_RATE_SERVICE_URL = "http://comment-rate-service:8000"
CUSTOMER_SERVICE_URL = "http://customer-service:8000"
ORDER_SERVICE_URL = "http://order-service:8000"
STAFF_SERVICE_URL = "http://staff-service:8000"

SERVICE_URLS = {
    "customer": "http://customer-service:8000",
    "book": "http://book-service:8000",
    "cart": "http://cart-service:8000",
    "staff": "http://staff-service:8000",
    "manager": "http://manager-service:8000",
    "catalog": "http://catalog-service:8000",
    "order": "http://order-service:8000",
    "ship": "http://ship-service:8000",
    "pay": "http://pay-service:8000",
    "rate": "http://comment-rate-service:8000",
    "recommend": "http://recommend-ai-service:8000",
}

MONEY_PLACES = Decimal("0.01")


def _base_context(request):
    return {
        "customer_id": request.session.get("customer_id"),
        "customer_name": request.session.get("customer_name"),
        "is_staff": request.session.get("is_staff", False),
    }


def _get_customer_id(request):
    customer_id = request.session.get("customer_id")
    if customer_id in (None, ""):
        return None
    try:
        return int(customer_id)
    except (TypeError, ValueError):
        return None


def _set_customer_session(request, customer):
    if not customer:
        return
    customer_id = customer.get("id")
    if customer_id is not None:
        request.session["customer_id"] = customer_id
    name = customer.get("name")
    if name:
        request.session["customer_name"] = name


def _safe_json(response):
    try:
        return response.json()
    except ValueError:
        return None


def _fetch_books(messages_target=None):
    try:
        response = requests.get(f"{BOOK_SERVICE_URL}/books/", timeout=3)
    except requests.RequestException:
        if messages_target is not None:
            messages.error(messages_target, "book-service unavailable")
        return []

    if response.status_code != 200:
        if messages_target is not None:
            messages.error(messages_target, "book-service unavailable")
        return []

    data = _safe_json(response)
    return data or []


def _fetch_cart_items(customer_id, messages_target=None):
    try:
        response = requests.get(
            f"{CART_SERVICE_URL}/carts/{customer_id}/",
            timeout=3,
        )
    except requests.RequestException:
        if messages_target is not None:
            messages.error(messages_target, "cart-service unavailable")
        return []

    if response.status_code != 200:
        if messages_target is not None:
            messages.error(messages_target, "cart-service unavailable")
        return []

    data = _safe_json(response)
    return data or []


def _map_cart_items(cart_items, books):
    book_map = {book.get("id"): book for book in books}
    total = Decimal("0.00")
    for item in cart_items:
        book = book_map.get(item.get("book_id"))
        item["book"] = book
        try:
            price = Decimal(str(book.get("price"))) if book else Decimal("0.00")
        except (TypeError, InvalidOperation):
            price = Decimal("0.00")
        line_total = price * Decimal(item.get("quantity", 0))
        line_total = line_total.quantize(MONEY_PLACES)
        item["line_total"] = line_total
        total += line_total
    total = total.quantize(MONEY_PLACES)
    return cart_items, total


def home(request):
    customer_id_param = request.GET.get("customer_id", "").strip()
    if customer_id_param:
        try:
            request.session["customer_id"] = int(customer_id_param)
        except (TypeError, ValueError):
            messages.error(request, "Customer id must be a number")

    search = request.GET.get("q", "").strip()
    author_filter = request.GET.get("author", "").strip()

    books = _fetch_books(messages_target=request)

    if search:
        search_lower = search.lower()
        books = [
            book
            for book in books
            if search_lower in str(book.get("title", "")).lower()
            or search_lower in str(book.get("author", "")).lower()
        ]

    if author_filter:
        books = [book for book in books if str(book.get("author", "")) == author_filter]

    authors = sorted({book.get("author") for book in books if book.get("author")})

    context = {
        **_base_context(request),
        "books": books,
        "search": search,
        "author_filter": author_filter,
        "authors": authors,
    }
    return render(request, "home.html", context)


def register(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "").strip()
        confirm_password = request.POST.get("confirm_password", "").strip()

        if not name or not email:
            messages.error(request, "Tên và email là bắt buộc.")
            return render(request, "register.html", {**_base_context(request)})

        if password or confirm_password:
            if password != confirm_password:
                messages.error(request, "Mật khẩu xác nhận không khớp.")
                return render(request, "register.html", {**_base_context(request)})

        payload = {
            "name": name,
            "email": email,
            "password": password if password else "",
        }

        try:
            response = requests.post(
                f"{CUSTOMER_SERVICE_URL}/customers/",
                json=payload,
                timeout=3,
            )
        except requests.RequestException:
            messages.error(request, "customer-service unavailable")
            return render(request, "register.html", {**_base_context(request)})

        if response.status_code not in {200, 201}:
            error_payload = _safe_json(response)
            messages.error(
                request,
                error_payload.get("error") if isinstance(error_payload, dict) else "Đăng ký thất bại.",
            )
            return render(request, "register.html", {**_base_context(request)})

        customer = _safe_json(response) or {}
        _set_customer_session(request, customer)
        request.session["is_staff"] = False
        messages.success(request, "Đăng ký thành công! Giỏ hàng của bạn đã sẵn sàng.")
        return redirect("cart")

    return render(request, "register.html", {**_base_context(request)})


def login_view(request):
    if request.method == "POST":
        customer_id = request.POST.get("customer_id", "").strip()
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "").strip()

        if customer_id:
            try:
                request.session["customer_id"] = int(customer_id)
                request.session["customer_name"] = ""
                messages.success(request, "Đăng nhập thành công.")
                next_url = request.GET.get("next") or reverse("home")
                return redirect(next_url)
            except (TypeError, ValueError):
                messages.error(request, "Customer id phải là số.")
                return render(request, "login.html", {**_base_context(request)})

        if email:
            if not password:
                messages.error(request, "Vui lòng nhập mật khẩu.")
                return render(request, "login.html", {**_base_context(request)})

            # First try staff login with JWT
            try:
                response = requests.post(
                    f"{STAFF_SERVICE_URL}/login/",
                    json={"email": email, "password": password},
                    timeout=3,
                )
            except requests.RequestException:
                response = None

            if response and response.status_code == 200:
                staff_data = _safe_json(response) or {}
                if staff_data:
                    request.session["customer_id"] = staff_data.get("id")
                    request.session["customer_name"] = staff_data.get("name", "")
                    request.session["is_staff"] = True
                    request.session["access_token"] = staff_data.get("access")
                    request.session["refresh_token"] = staff_data.get("refresh")
                    request.session["user_type"] = "staff"
                    messages.success(request, "Đăng nhập staff thành công.")
                    next_url = request.GET.get("next") or reverse("staff_books")
                    return redirect(next_url)

            # Fall back to customer login with JWT
            try:
                response = requests.post(
                    f"{CUSTOMER_SERVICE_URL}/login/",
                    json={"email": email, "password": password},
                    timeout=3,
                )
            except requests.RequestException:
                messages.error(request, "customer-service unavailable")
                return render(request, "login.html", {**_base_context(request)})

            if response.status_code == 200:
                customer_data = _safe_json(response) or {}
                if customer_data:
                    request.session["customer_id"] = customer_data.get("id")
                    request.session["customer_name"] = customer_data.get("name", "")
                    request.session["is_staff"] = False
                    request.session["access_token"] = customer_data.get("access")
                    request.session["refresh_token"] = customer_data.get("refresh")
                    request.session["user_type"] = "customer"
                    messages.success(request, "Đăng nhập thành công.")
                    next_url = request.GET.get("next") or reverse("home")
                    return redirect(next_url)
            
            error_response = _safe_json(response)
            error_msg = error_response.get("error") if isinstance(error_response, dict) else "Không tìm thấy tài khoản hoặc mật khẩu không đúng."
            messages.error(request, error_msg)
            return render(request, "login.html", {**_base_context(request)})

        messages.error(request, "Vui lòng nhập email và mật khẩu.")

    return render(request, "login.html", {**_base_context(request)})


def logout_view(request):
    request.session.pop("customer_id", None)
    request.session.pop("customer_name", None)
    request.session.pop("is_staff", None)
    request.session.pop("access_token", None)
    request.session.pop("refresh_token", None)
    request.session.pop("user_type", None)
    messages.success(request, "Đã đăng xuất.")
    return redirect("home")


def cart_view(request):
    customer_id = _get_customer_id(request)
    if not customer_id:
        messages.error(request, "Vui lòng đăng nhập để xem giỏ hàng.")
        return redirect("login")

    books = _fetch_books(messages_target=request)
    cart_items = _fetch_cart_items(customer_id, messages_target=request)
    cart_items, total = _map_cart_items(cart_items, books)

    context = {
        **_base_context(request),
        "cart_items": cart_items,
        "total": total,
    }
    return render(request, "cart.html", context)


def add_to_cart(request):
    if request.method != "POST":
        return redirect("home")

    customer_id = request.POST.get("customer_id", "").strip()
    book_id = request.POST.get("book_id", "").strip()
    quantity = request.POST.get("quantity", "1").strip()

    if not customer_id:
        customer_id = _get_customer_id(request)
    if not customer_id:
        messages.error(request, "Vui lòng đăng nhập để thêm vào giỏ.")
        return redirect("login")

    payload = {
        "customer_id": customer_id,
        "book_id": book_id,
        "quantity": quantity,
    }

    try:
        response = requests.post(
            f"{CART_SERVICE_URL}/cart-items/",
            json=payload,
            timeout=3,
        )
    except requests.RequestException:
        messages.error(request, "cart-service unavailable")
        return redirect("home")

    if response.status_code != 200:
        messages.error(request, "Không thể thêm vào giỏ.")
        return redirect("home")

    messages.success(request, "Đã thêm vào giỏ hàng.")
    return redirect("cart")


def update_cart_item(request, item_id):
    if request.method != "POST":
        return redirect("cart")

    quantity = request.POST.get("quantity", "").strip()
    if not quantity:
        return redirect("cart")

    payload = {"quantity": quantity}
    try:
        response = requests.patch(
            f"{CART_SERVICE_URL}/cart-items/{item_id}/",
            json=payload,
            timeout=3,
        )
    except requests.RequestException:
        messages.error(request, "cart-service unavailable")
        return redirect("cart")

    if response.status_code not in {200, 204}:
        messages.error(request, "Không thể cập nhật giỏ hàng.")
        return redirect("cart")

    messages.success(request, "Đã cập nhật giỏ hàng.")
    return redirect("cart")


def delete_cart_item(request, item_id):
    if request.method != "POST":
        return redirect("cart")

    try:
        response = requests.delete(
            f"{CART_SERVICE_URL}/cart-items/{item_id}/",
            timeout=3,
        )
    except requests.RequestException:
        messages.error(request, "cart-service unavailable")
        return redirect("cart")

    if response.status_code not in {200, 204}:
        messages.error(request, "Không thể xóa sản phẩm.")
        return redirect("cart")

    messages.success(request, "Đã xóa sản phẩm khỏi giỏ.")
    return redirect("cart")


def book_detail(request, book_id):
    customer_id = _get_customer_id(request)
    
    try:
        book_response = requests.get(
            f"{BOOK_SERVICE_URL}/books/{book_id}/",
            timeout=3,
        )
    except requests.RequestException:
        messages.error(request, "book-service unavailable")
        return redirect("home")

    if book_response.status_code == 404:
        return HttpResponse("Book not found", status=404)

    if book_response.status_code != 200:
        messages.error(request, "book-service unavailable")
        return redirect("home")

    book = _safe_json(book_response) or {}

    try:
        ratings_response = requests.get(
            f"{COMMENT_RATE_SERVICE_URL}/ratings/",
            params={"book_id": book_id},
            timeout=3,
        )
        ratings = _safe_json(ratings_response) or []
    except requests.RequestException:
        ratings = []

    try:
        recommend_response = requests.get(
            f"{SERVICE_URLS['recommend']}/recommend/{book_id}/",
            params={"user_id": customer_id} if customer_id else {},
            timeout=3,
        )
        recommendations = _safe_json(recommend_response) or []
    except requests.RequestException:
        recommendations = []

    # Avoid passing invalid IDs into the template url tag (Django will raise NoReverseMatch).
    if isinstance(recommendations, list):
        recommendations = [r for r in recommendations if isinstance(r, dict) and r.get("id")]
    else:
        # If the recommendation service returns errors (dict) or unexpected data, ignore it.
        recommendations = []

    context = {
        **_base_context(request),
        "book": book,
        "ratings": ratings,
        "recommendations": recommendations,
    }
    return render(request, "book_detail.html", context)


def rate_book(request, book_id):
    if request.method != "POST":
        return redirect("book_detail", book_id=book_id)

    rating = request.POST.get("rating", "").strip()
    comment = request.POST.get("comment", "").strip()
    customer_id = _get_customer_id(request)

    if not customer_id:
        messages.error(request, "Vui lòng đăng nhập để đánh giá.")
        return redirect("login")

    payload = {
        "rating": rating,
        "comment": comment,
        "customer_id": customer_id,
    }

    try:
        response = requests.post(
            f"{COMMENT_RATE_SERVICE_URL}/books/{book_id}/rate/",
            json=payload,
            timeout=3,
        )
    except requests.RequestException:
        messages.error(request, "comment-rate-service unavailable")
        return redirect("book_detail", book_id=book_id)

    if response.status_code == 400:
        error_data = _safe_json(response)
        if error_data and error_data.get("error") == "You have already rated this book":
            messages.error(request, "Bạn đã đánh giá sách này rồi.")
        else:
            messages.error(request, "Không thể gửi đánh giá.")
        return redirect("book_detail", book_id=book_id)
    elif response.status_code != 200:
        messages.error(request, "Không thể gửi đánh giá.")
        return redirect("book_detail", book_id=book_id)

    messages.success(request, "Cảm ơn bạn đã đánh giá!")
    return redirect("book_detail", book_id=book_id)


def checkout(request):
    customer_id = _get_customer_id(request)
    if not customer_id:
        messages.error(request, "Vui lòng đăng nhập để thanh toán.")
        return redirect("login")

    books = _fetch_books(messages_target=request)
    cart_items = _fetch_cart_items(customer_id, messages_target=request)
    cart_items, total = _map_cart_items(cart_items, books)

    if request.method == "POST":
        shipping_address = request.POST.get("shipping_address", "").strip()
        payment_method = request.POST.get("payment_method", "").strip()
        shipping_method = request.POST.get("shipping_method", "").strip()

        if not shipping_address:
            messages.error(request, "Vui lòng nhập địa chỉ giao hàng.")
        else:
            payload = {
                "customer_id": customer_id,
                "payment_method": payment_method,
                "shipping_method": shipping_method,
                "shipping_address": shipping_address,
            }
            try:
                response = requests.post(
                    f"{ORDER_SERVICE_URL}/orders/",
                    json=payload,
                    timeout=5,
                )
            except requests.RequestException:
                messages.error(request, "order-service unavailable")
                response = None

            if response is not None and response.status_code == 201:
                order = _safe_json(response) or {}
                messages.success(request, "Đặt hàng thành công!")
                context = {
                    **_base_context(request),
                    "order": order,
                    "cart_items": cart_items,
                    "total": total,
                    "just_created": True,
                }
                return render(request, "order_success.html", context)

            if response is not None:
                error_payload = _safe_json(response)
                error_message = (
                    error_payload.get("error") if isinstance(error_payload, dict) else "Đặt hàng thất bại."
                )
                messages.error(request, error_message)

    context = {
        **_base_context(request),
        "cart_items": cart_items,
        "total": total,
        "payment_methods": [
            {"value": "cod", "label": "Thanh toán khi nhận hàng (COD)"},
            {"value": "card", "label": "Thẻ tín dụng"},
            {"value": "ewallet", "label": "Ví điện tử"},
        ],
        "shipping_methods": [
            {"value": "express", "label": "Giao hàng nhanh"},
            {"value": "economy", "label": "Giao hàng tiết kiệm"},
        ],
    }
    return render(request, "checkout.html", context)


def orders(request):
    customer_id = _get_customer_id(request)
    if not customer_id:
        messages.error(request, "Vui lòng đăng nhập để xem đơn hàng.")
        return redirect("login")

    try:
        response = requests.get(
            f"{ORDER_SERVICE_URL}/orders/",
            params={"customer_id": customer_id},
            timeout=3,
        )
    except requests.RequestException:
        messages.error(request, "order-service unavailable")
        return redirect("home")

    if response.status_code != 200:
        messages.error(request, "Không thể lấy danh sách đơn hàng.")
        return redirect("home")

    orders = _safe_json(response) or []
    context = {
        **_base_context(request),
        "orders": orders,
    }
    return render(request, "orders.html", context)


def order_success(request, order_id):
    try:
        response = requests.get(
            f"{ORDER_SERVICE_URL}/orders/{order_id}/",
            timeout=3,
        )
    except requests.RequestException:
        messages.error(request, "order-service unavailable")
        return redirect("home")

    if response.status_code != 200:
        messages.error(request, "Không tìm thấy đơn hàng.")
        return redirect("home")

    order = _safe_json(response) or {}
    customer_id = _get_customer_id(request)
    if customer_id:
        try:
            order_customer_id = int(order.get("customer_id"))
        except (TypeError, ValueError):
            order_customer_id = None
        if order_customer_id != customer_id:
            messages.error(request, "Không tìm thấy đơn hàng.")
            return redirect("home")

    context = {
        **_base_context(request),
        "order": order,
        "just_created": False,
    }
    return render(request, "order_success.html", context)


def staff_books(request):
    if not request.session.get("is_staff"):
        messages.error(request, "Bạn cần đăng nhập staff để quản lý sách.")
        return redirect("login")

    books = []
    try:
        response = requests.get(
            f"{STAFF_SERVICE_URL}/books/",
            timeout=3,
        )
        if response.status_code == 200:
            books = _safe_json(response) or []
        else:
            messages.error(request, "staff-service unavailable")
    except requests.RequestException:
        messages.error(request, "staff-service unavailable")

    context = {
        **_base_context(request),
        "books": books,
    }
    return render(request, "staff_books.html", context)


def staff_book_create(request):
    if request.method != "POST":
        return redirect("staff_books")

    if not request.session.get("is_staff"):
        messages.error(request, "Bạn cần đăng nhập staff để quản lý sách.")
        return redirect("login")

    payload = {
        "title": request.POST.get("title", "").strip(),
        "author": request.POST.get("author", "").strip(),
        "price": request.POST.get("price", "").strip(),
        "stock": request.POST.get("stock", "").strip(),
        "image_url": request.POST.get("image_url", "").strip(),
    }

    try:
        response = requests.post(
            f"{STAFF_SERVICE_URL}/books/",
            json=payload,
            timeout=3,
        )
    except requests.RequestException:
        messages.error(request, "staff-service unavailable")
        return redirect("staff_books")

    if response.status_code not in {200, 201}:
        messages.error(request, "Không thể thêm sách.")
        return redirect("staff_books")

    messages.success(request, "Đã thêm sách mới.")
    return redirect("staff_books")


def staff_book_update(request, book_id):
    if request.method != "POST":
        return redirect("staff_books")

    if not request.session.get("is_staff"):
        messages.error(request, "Bạn cần đăng nhập staff để quản lý sách.")
        return redirect("login")

    payload = {
        "title": request.POST.get("title", "").strip(),
        "author": request.POST.get("author", "").strip(),
        "price": request.POST.get("price", "").strip(),
        "stock": request.POST.get("stock", "").strip(),
        "image_url": request.POST.get("image_url", "").strip(),
    }

    try:
        response = requests.patch(
            f"{STAFF_SERVICE_URL}/books/{book_id}/",
            json=payload,
            timeout=3,
        )
    except requests.RequestException:
        messages.error(request, "staff-service unavailable")
        return redirect("staff_books")

    if response.status_code != 200:
        messages.error(request, "Không thể cập nhật sách.")
        return redirect("staff_books")

    messages.success(request, "Đã cập nhật sách.")
    return redirect("staff_books")


def staff_book_delete(request, book_id):
    if request.method != "POST":
        return redirect("staff_books")

    if not request.session.get("is_staff"):
        messages.error(request, "Bạn cần đăng nhập staff để quản lý sách.")
        return redirect("login")

    try:
        response = requests.delete(
            f"{STAFF_SERVICE_URL}/books/{book_id}/",
            timeout=3,
        )
    except requests.RequestException:
        messages.error(request, "staff-service unavailable")
        return redirect("staff_books")

    if response.status_code not in {200, 204}:
        messages.error(request, "Không thể xóa sách.")
        return redirect("staff_books")

    messages.success(request, "Đã xóa sách.")
    return redirect("staff_books")


def staff_orders(request):
    """Trang quản lý đơn hàng cho staff"""
    if not request.session.get("is_staff"):
        messages.error(request, "Bạn cần đăng nhập staff để quản lý đơn hàng.")
        return redirect("login")

    # Lấy filter từ query params
    status_filter = request.GET.get("status", "pending")
    
    try:
        if status_filter == "pending":
            # Lấy đơn hàng chờ duyệt
            response = requests.get(
                f"{ORDER_SERVICE_URL}/orders/pending/",
                timeout=3,
            )
        else:
            # Lấy tất cả đơn hàng và filter theo status
            response = requests.get(
                f"{ORDER_SERVICE_URL}/orders/",
                timeout=3,
            )
    except requests.RequestException:
        messages.error(request, "order-service unavailable")
        return redirect("staff_books")

    if response.status_code != 200:
        messages.error(request, "Không thể lấy danh sách đơn hàng.")
        return redirect("staff_books")

    orders = _safe_json(response) or []
    
    # Filter orders nếu không phải pending
    if status_filter != "pending" and status_filter != "all":
        orders = [order for order in orders if order.get("status") == status_filter]

    context = {
        **_base_context(request),
        "orders": orders,
        "status_filter": status_filter,
        "status_options": [
            {"value": "pending", "label": "Chờ duyệt"},
            {"value": "all", "label": "Tất cả"},
            {"value": "processing", "label": "Đang xử lý"},
            {"value": "confirmed", "label": "Đã xác nhận"},
            {"value": "shipped", "label": "Đã giao vận"},
            {"value": "delivered", "label": "Đã giao hàng"},
            {"value": "cancelled", "label": "Đã hủy"},
        ]
    }
    return render(request, "staff_orders.html", context)


def staff_order_detail(request, order_id):
    """Chi tiết đơn hàng cho staff"""
    if not request.session.get("is_staff"):
        messages.error(request, "Bạn cần đăng nhập staff để quản lý đơn hàng.")
        return redirect("login")

    try:
        response = requests.get(
            f"{ORDER_SERVICE_URL}/orders/{order_id}/approval/",
            timeout=3,
        )
    except requests.RequestException:
        messages.error(request, "order-service unavailable")
        return redirect("staff_orders")

    if response.status_code == 404:
        messages.error(request, "Không tìm thấy đơn hàng.")
        return redirect("staff_orders")

    if response.status_code != 200:
        messages.error(request, "Không thể lấy thông tin đơn hàng.")
        return redirect("staff_orders")

    order = _safe_json(response) or {}
    
    context = {
        **_base_context(request),
        "order": order,
        "approval_status_options": [
            {"value": "pending", "label": "Chờ duyệt"},
            {"value": "approved", "label": "Đã duyệt"},
            {"value": "rejected", "label": "Đã từ chối"},
        ],
        "order_status_options": [
            {"value": "pending", "label": "Chờ xử lý"},
            {"value": "processing", "label": "Đang xử lý"},
            {"value": "confirmed", "label": "Đã xác nhận"},
            {"value": "shipped", "label": "Đã giao vận"},
            {"value": "delivered", "label": "Đã giao hàng"},
            {"value": "cancelled", "label": "Đã hủy"},
            {"value": "failed", "label": "Thất bại"},
        ]
    }
    return render(request, "staff_order_detail.html", context)


def staff_order_approve(request, order_id):
    """Duyệt đơn hàng"""
    if request.method != "POST":
        return redirect("staff_order_detail", order_id=order_id)

    if not request.session.get("is_staff"):
        messages.error(request, "Bạn cần đăng nhập staff để duyệt đơn hàng.")
        return redirect("login")

    action = request.POST.get("action", "").strip()
    staff_id = request.session.get("customer_id")  # staff_id stored in customer_id session
    
    if not staff_id:
        messages.error(request, "Không thể xác định staff.")
        return redirect("staff_order_detail", order_id=order_id)

    payload = {
        "action": action,
        "staff_id": staff_id,
    }

    if action == "approve":
        tracking_number = request.POST.get("tracking_number", "").strip()
        estimated_delivery = request.POST.get("estimated_delivery", "").strip()
        notes = request.POST.get("notes", "").strip()
        
        if tracking_number:
            payload["tracking_number"] = tracking_number
        if estimated_delivery:
            payload["estimated_delivery"] = estimated_delivery
        if notes:
            payload["notes"] = notes
            
    elif action == "reject":
        rejection_reason = request.POST.get("rejection_reason", "").strip()
        if rejection_reason:
            payload["rejection_reason"] = rejection_reason

    try:
        response = requests.post(
            f"{ORDER_SERVICE_URL}/orders/{order_id}/approval/",
            json=payload,
            timeout=3,
        )
    except requests.RequestException:
        messages.error(request, "order-service unavailable")
        return redirect("staff_order_detail", order_id=order_id)

    if response.status_code == 200:
        if action == "approve":
            messages.success(request, "Đã duyệt đơn hàng thành công.")
        else:
            messages.success(request, "Đã từ chối đơn hàng.")
    else:
        error_data = _safe_json(response)
        error_msg = error_data.get("error") if isinstance(error_data, dict) else "Không thể xử lý đơn hàng."
        messages.error(request, error_msg)

    return redirect("staff_order_detail", order_id=order_id)


def staff_order_update(request, order_id):
    """Cập nhật thông tin đơn hàng"""
    if request.method != "POST":
        return redirect("staff_order_detail", order_id=order_id)

    if not request.session.get("is_staff"):
        messages.error(request, "Bạn cần đăng nhập staff để cập nhật đơn hàng.")
        return redirect("login")

    payload = {}
    
    # Các trường có thể cập nhật
    fields = ["status", "tracking_number", "estimated_delivery", "notes"]
    for field in fields:
        value = request.POST.get(field, "").strip()
        if value:
            payload[field] = value

    if not payload:
        messages.warning(request, "Không có thông tin nào để cập nhật.")
        return redirect("staff_order_detail", order_id=order_id)

    try:
        response = requests.patch(
            f"{ORDER_SERVICE_URL}/orders/{order_id}/approval/",
            json=payload,
            timeout=3,
        )
    except requests.RequestException:
        messages.error(request, "order-service unavailable")
        return redirect("staff_order_detail", order_id=order_id)

    if response.status_code == 200:
        messages.success(request, "Đã cập nhật thông tin đơn hàng.")
    else:
        error_data = _safe_json(response)
        error_msg = error_data.get("error") if isinstance(error_data, dict) else "Không thể cập nhật đơn hàng."
        messages.error(request, error_msg)

    return redirect("staff_order_detail", order_id=order_id)


def _proxy_headers(request):
    headers = {}
    for key, value in request.headers.items():
        if key.lower() in {"host", "content-length"}:
            continue
        headers[key] = value
    return headers


@csrf_exempt
def api_login(request):
    """API endpoint for JWT login (JSON POST)"""
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    import json
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    
    email = data.get("email", "").strip().lower()
    password = data.get("password", "").strip()
    
    if not email or not password:
        return JsonResponse({"error": "Email and password required"}, status=400)
    
    # Try staff login first
    try:
        response = requests.post(
            f"{STAFF_SERVICE_URL}/login/",
            json={"email": email, "password": password},
            timeout=3,
        )
    except requests.RequestException:
        response = None
    
    if response and response.status_code == 200:
        staff_data = _safe_json(response) or {}
        return JsonResponse({
            "success": True,
            "user_type": "staff",
            "data": staff_data
        })
    
    # Fall back to customer login
    try:
        response = requests.post(
            f"{CUSTOMER_SERVICE_URL}/login/",
            json={"email": email, "password": password},
            timeout=3,
        )
    except requests.RequestException:
        return JsonResponse({"error": "customer-service unavailable"}, status=503)
    
    if response.status_code == 200:
        customer_data = _safe_json(response) or {}
        return JsonResponse({
            "success": True,
            "user_type": "customer",
            "data": customer_data
        })
    
    error_response = _safe_json(response) or {}
    error_msg = error_response.get("error", "Invalid credentials")
    return JsonResponse({"error": error_msg}, status=401)


@csrf_exempt
def api_proxy(request, service, resource_path=""):
    base_url = SERVICE_URLS.get(service)
    if not base_url:
        return JsonResponse({"error": "Unknown service"}, status=404)

    url = base_url if not resource_path else f"{base_url}/{resource_path}"

    try:
        response = requests.request(
            method=request.method,
            url=url,
            params=request.GET if request.GET else None,
            data=request.body if request.body else None,
            headers=_proxy_headers(request),
            timeout=5,
        )
    except requests.RequestException:
        return JsonResponse({"error": f"{service}-service unavailable"}, status=503)

    content_type = response.headers.get("Content-Type", "application/json")
    return HttpResponse(
        response.content,
        status=response.status_code,
        content_type=content_type,
    )
