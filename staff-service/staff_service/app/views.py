from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Staff
from .serializers import StaffSerializer
import requests

BOOK_SERVICE_URL = "http://book-service:8000"


class Health(APIView):
    def get(self, request):
        return Response({
            "service": "staff-service",
            "status": "ok",
        })


class StaffListCreate(APIView):
    def get(self, request):
        staffs = Staff.objects.all()
        serializer = StaffSerializer(staffs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = StaffSerializer(data=request.data)
        if serializer.is_valid():
            staff = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def _proxy_book_service(method, path, request):
    url = f"{BOOK_SERVICE_URL}{path}"
    try:
        response = requests.request(
            method,
            url,
            params=request.query_params if method == "get" else None,
            json=request.data if method in {"post", "put", "patch"} else None,
            timeout=3,
        )
    except requests.RequestException:
        return Response(
            {"error": "book-service unavailable"},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    if response.status_code == status.HTTP_204_NO_CONTENT:
        return Response(status=status.HTTP_204_NO_CONTENT)

    try:
        data = response.json()
    except ValueError:
        data = {"detail": response.text}

    return Response(data, status=response.status_code)


class StaffBookListCreate(APIView):
    def get(self, request):
        return _proxy_book_service("get", "/books/", request)

    def post(self, request):
        return _proxy_book_service("post", "/books/", request)


class StaffBookDetail(APIView):
    def get(self, request, book_id):
        return _proxy_book_service("get", f"/books/{book_id}/", request)

    def patch(self, request, book_id):
        return _proxy_book_service("patch", f"/books/{book_id}/", request)

    def delete(self, request, book_id):
        return _proxy_book_service("delete", f"/books/{book_id}/", request)


class StaffBookDetail(APIView):
    def get(self, request, book_id):
        return _proxy_book_service("get", f"/books/{book_id}/", request)

    def put(self, request, book_id):
        return _proxy_book_service("put", f"/books/{book_id}/", request)

    def patch(self, request, book_id):
        return _proxy_book_service("patch", f"/books/{book_id}/", request)

    def delete(self, request, book_id):
        return _proxy_book_service("delete", f"/books/{book_id}/", request)
