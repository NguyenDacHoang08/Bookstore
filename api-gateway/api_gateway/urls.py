"""
URL configuration for api_gateway project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("cart/", views.cart_view, name="cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("orders/<int:order_id>/", views.order_success, name="order_success"),
    path("books/<int:book_id>/", views.book_detail, name="book_detail"),
    path("books/<int:book_id>/rate/", views.rate_book, name="rate_book"),
    path("cart/add/", views.add_to_cart, name="add_to_cart"),
    path("cart/items/<int:item_id>/update/", views.update_cart_item, name="update_cart_item"),
    path("cart/items/<int:item_id>/delete/", views.delete_cart_item, name="delete_cart_item"),
    path("staff/books/", views.staff_books, name="staff_books"),
    path("staff/books/create/", views.staff_book_create, name="staff_book_create"),
    path("staff/books/<int:book_id>/update/", views.staff_book_update, name="staff_book_update"),
    path("staff/books/<int:book_id>/delete/", views.staff_book_delete, name="staff_book_delete"),
    path("api/<str:service>/", views.api_proxy, name="api_proxy_root"),
    path("api/<str:service>/<path:resource_path>/", views.api_proxy, name="api_proxy"),
]
