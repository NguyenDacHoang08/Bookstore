from django.db import models

class Customer(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # For hashed password
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)