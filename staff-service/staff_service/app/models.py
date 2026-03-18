from django.db import models

class Staff(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # For hashed password
    role = models.CharField(max_length=50, default='staff')  # staff, manager, etc.
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)