from django.db import models


class Shipment(models.Model):
    order_id = models.IntegerField()
    method = models.CharField(max_length=50)
    address = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, default="created")
    created_at = models.DateTimeField(auto_now_add=True)
