from django.db import models
class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    rating_avg = models.FloatField(default=0)
    rating_count = models.IntegerField(default=0)
    image_url = models.URLField(blank=True, null=True)
