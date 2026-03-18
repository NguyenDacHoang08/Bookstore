from django.db import models


class Rating(models.Model):
    customer_id = models.IntegerField(null=True, blank=True)
    book_id = models.IntegerField()
    rating = models.IntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('customer_id', 'book_id')
