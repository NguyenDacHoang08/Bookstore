import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from django.contrib.auth.hashers import make_password

BOOK_SERVICE_URL = os.environ.get("BOOK_SERVICE_URL", "http://localhost:8002")
CUSTOMER_SERVICE_URL = os.environ.get("CUSTOMER_SERVICE_URL", "http://localhost:8001")
CART_SERVICE_URL = os.environ.get("CART_SERVICE_URL", "http://localhost:8003")
RATE_SERVICE_URL = os.environ.get("RATE_SERVICE_URL", "http://localhost:8010")
ORDER_SERVICE_URL = os.environ.get("ORDER_SERVICE_URL", "http://localhost:8007")
STAFF_SERVICE_URL = os.environ.get("STAFF_SERVICE_URL", "http://localhost:8004")

DEFAULT_TIMEOUT = 5

BOOKS = [
    {
        "title": "Service Patterns 101",
        "author": "Lea Nguyen",
        "price": "15.90",
        "stock": 40,
    },
    {
        "title": "Gateway Design",
        "author": "Minh Pham",
        "price": "19.50",
        "stock": 22,
    },
    {
        "title": "Eventful Retail",
        "author": "Quang Tran",
        "price": "12.75",
        "stock": 35,
    },
    {
        "title": "Data Consistency",
        "author": "An Ho",
        "price": "18.25",
        "stock": 15,
    },
    {
        "title": "Saga Journeys",
        "author": "Bao Pham",
        "price": "21.00",
        "stock": 18,
    },
    {
        "title": "Microservice Security",
        "author": "Lan Vo",
        "price": "17.80",
        "stock": 25,
    },
    {
        "title": "Scaling Django",
        "author": "Hieu Le",
        "price": "16.40",
        "stock": 30,
    },
    {
        "title": "Async Python in Practice",
        "author": "Thuy Pham",
        "price": "14.20",
        "stock": 28,
    },
]

CUSTOMERS = [
    {"name": "Alice Tran", "email": "alice@example.com", "password": "password123"},
    {"name": "Bao Nguyen", "email": "bao@example.com", "password": "password123"},
]

STAFFS = [
    {"name": "Staff One", "email": "staff@example.com", "password": "staff123", "role": "staff"},
]


def request_json(method, url, payload=None, timeout=DEFAULT_TIMEOUT):
    data = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = Request(url, data=data, method=method, headers=headers)
    try:
        with urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
            if raw:
                try:
                    return response.status, json.loads(raw)
                except json.JSONDecodeError:
                    return response.status, raw
            return response.status, None
    except HTTPError as error:
        raw = error.read().decode("utf-8")
        try:
            return error.code, json.loads(raw)
        except json.JSONDecodeError:
            return error.code, raw
    except URLError as error:
        return None, {"error": str(error)}


def fetch_list(url):
    status, data = request_json("GET", url)
    if status and 200 <= status < 300 and isinstance(data, list):
        return data
    return []


def seed_books():
    existing = fetch_list(f"{BOOK_SERVICE_URL}/books/")
    existing_keys = {
        (str(book.get("title", "")).lower(), str(book.get("author", "")).lower())
        for book in existing
    }

    created = []
    for book in BOOKS:
        key = (book["title"].lower(), book["author"].lower())
        if key in existing_keys:
            continue
        status, data = request_json("POST", f"{BOOK_SERVICE_URL}/books/", book)
        if status in {200, 201}:
            created.append(data)
        else:
            print("Failed to create book:", book["title"], "status=", status)

    all_books = fetch_list(f"{BOOK_SERVICE_URL}/books/")
    print(f"Books available: {len(all_books)} (created {len(created)})")
    return all_books


def seed_customers():
    existing = fetch_list(f"{CUSTOMER_SERVICE_URL}/customers/")
    existing_by_email = {str(customer.get("email", "")).lower(): customer for customer in existing}
    created = []

    for customer in CUSTOMERS:
        email = customer["email"].lower()
        if email in existing_by_email:
            continue
        status, data = request_json(
            "POST",
            f"{CUSTOMER_SERVICE_URL}/customers/",
            customer,
        )
        if status in {200, 201}:
            created.append(data)
        else:
            print("Failed to create customer:", customer["email"], "status=", status)

    all_customers = fetch_list(f"{CUSTOMER_SERVICE_URL}/customers/")
    print(f"Customers available: {len(all_customers)} (created {len(created)})")
    return all_customers


def seed_staffs():
    existing = fetch_list(f"{STAFF_SERVICE_URL}/staffs/")
    existing_by_email = {str(staff.get("email", "")).lower(): staff for staff in existing}
    created = []

    for staff in STAFFS:
        email = staff["email"].lower()
        if email in existing_by_email:
            continue
        status, data = request_json(
            "POST",
            f"{STAFF_SERVICE_URL}/staffs/",
            staff,
        )
        if status in {200, 201}:
            created.append(data)
        else:
            print("Failed to create staff:", staff["email"], "status=", status)

    all_staffs = fetch_list(f"{STAFF_SERVICE_URL}/staffs/")
    print(f"Staffs available: {len(all_staffs)} (created {len(created)})")
    return all_staffs


def add_cart_item(customer_id, book_id, quantity):
    payload = {
        "customer_id": customer_id,
        "book_id": book_id,
        "quantity": quantity,
    }
    status, data = request_json("POST", f"{CART_SERVICE_URL}/cart-items/", payload)
    if status in {200, 201}:
        return data
    print("Failed to add cart item", payload, "status=", status)
    return None


def seed_cart(customers, books):
    if not customers or not books:
        return

    customer_one = customers[0]
    customer_two = customers[1] if len(customers) > 1 else None

    if customer_one:
        add_cart_item(customer_one.get("id"), books[0].get("id"), 2)
        add_cart_item(customer_one.get("id"), books[1].get("id"), 1)
        add_cart_item(customer_one.get("id"), books[2].get("id"), 3)

    if customer_two:
        add_cart_item(customer_two.get("id"), books[2].get("id"), 1)
        add_cart_item(customer_two.get("id"), books[3].get("id"), 1)

    print("Cart items seeded.")


def rating_exists(book_id, customer_id):
    ratings = fetch_list(f"{RATE_SERVICE_URL}/ratings/?book_id={book_id}")
    for rating in ratings:
        if rating.get("customer_id") == customer_id:
            return True
    return False


def seed_ratings(customers, books):
    if not customers or not books:
        return

    customer = customers[0]
    comments = [
        "Great starter for microservices.",
        "Clear and practical UI gateway tips.",
        "Useful patterns and examples.",
        "Well explained and approachable.",
        "In-depth and practical.",
        "Excellent coverage of security.",
        "Perfect for scaling Django apps.",
        "Async patterns made simple.",
    ]

    created = 0
    for idx, book in enumerate(books):
        payload = {
            "book_id": book.get("id"),
            "customer_id": customer.get("id"),
            "rating": 5 - (idx % 3),
            "comment": comments[idx % len(comments)],
        }

        if rating_exists(payload["book_id"], payload["customer_id"]):
            continue

        status, _ = request_json(
            "POST",
            f"{RATE_SERVICE_URL}/books/{payload['book_id']}/rate/",
            payload,
        )
        if status == 200:
            created += 1
        else:
            print("Failed to create rating for book", payload["book_id"], "status=", status)

    print(f"Ratings created: {created}")


def seed_order(customer):
    if not customer:
        return

    payload = {
        "customer_id": customer.get("id"),
        "payment_method": "cod",
        "shipping_method": "express",
        "shipping_address": "123 Sample Street, District 1",
    }
    status, data = request_json("POST", f"{ORDER_SERVICE_URL}/orders/", payload, timeout=10)
    if status == 201:
        print("Order created:", data.get("id"))
    else:
        print("Order not created (cart may be empty). status=", status)


def main():
    print("Seeding sample data...")
    books = seed_books()
    customers = seed_customers()
    staffs = seed_staffs()
    seed_cart(customers, books)
    seed_ratings(customers, books)
    if customers:
        seed_order(customers[0])
    print("Done.")


if __name__ == "__main__":
    main()
