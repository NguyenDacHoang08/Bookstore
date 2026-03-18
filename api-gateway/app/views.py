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
            "password": make_password(password) if password else "",
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

            # First try staff login (default staff account)
            try:
                response = requests.get(
                    f"{STAFF_SERVICE_URL}/staffs/",
                    timeout=3,
                )
            except requests.RequestException:
                response = None

            if response and response.status_code == 200:
                staffs = _safe_json(response) or []
                match = next(
                    (staff for staff in staffs if staff.get("email", "").lower() == email),
                    None,
                )
                if match:
                    if password and not check_password(password, match.get("password", "")):
                        messages.error(request, "Mật khẩu không đúng.")
                        return render(request, "login.html", {**_base_context(request)})

                    _set_customer_session(request, match)
                    request.session["is_staff"] = True
                    messages.success(request, "Đăng nhập staff thành công.")
                    next_url = request.GET.get("next") or reverse("staff_books")
                    return redirect(next_url)

            # Fall back to customer login
            try:
                response = requests.get(
                    f"{CUSTOMER_SERVICE_URL}/customers/",
                    timeout=3,
                )
            except requests.RequestException:
                messages.error(request, "customer-service unavailable")
                return render(request, "login.html", {**_base_context(request)})

            if response.status_code != 200:
                messages.error(request, "customer-service unavailable")
                return render(request, "login.html", {**_base_context(request)})

            customers = _safe_json(response) or []
            match = next(
                (customer for customer in customers if customer.get("email", "").lower() == email),
                None,
            )
            if not match:
                messages.error(request, "Không tìm thấy tài khoản.")
                return render(request, "login.html", {**_base_context(request)})

            if password and not check_password(password, match.get("password", "")):
                messages.error(request, "Mật khẩu không đúng.")
                return render(request, "login.html", {**_base_context(request)})

            _set_customer_session(request, match)
            messages.success(request, "Đăng nhập thành công.")
            next_url = request.GET.get("next") or reverse("home")
            return redirect(next_url)

        messages.error(request, "Vui lòng nhập email và mật khẩu.")

    return render(request, "login.html", {**_base_context(request)})


def logout_view(request):
    request.session.pop("customer_id", None)
    request.session.pop("customer_name", None)
    request.session.pop("is_staff", None)
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
            timeout=3,
        )
        recommendations = _safe_json(recommend_response) or []
    except requests.RequestException:
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
    context = {
        **_base_context(request),
        "order": order,
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


def _proxy_headers(request):
    headers = {}
    for key, value in request.headers.items():
        if key.lower() in {"host", "content-length"}:
            continue
        headers[key] = value
    return headers


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
