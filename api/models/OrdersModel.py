from django.db import models
from api.models import *
from django.contrib.auth.models import User


class Order(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    address = models.ForeignKey(
        addresses, on_delete=models.DO_NOTHING, null=True, blank=True)

    def __str__(self):
        return f'Order #{self.id}'


class OrderItem(models.Model):
    STATUS_CHOICES = (
        ("Confirmed", "confirmed"),
        ("Cancelled", "cancelled"),
        ("Processing", "processing")
    )
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(products, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    item_price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True)
    order_status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="Processing")

    def __str__(self):
        return f'{self.quantity} x {self.product.title}'

    def save(self, *args, **kwargs):
        self.item_price = self.product.sold_price * self.quantity
        super().save(*args, **kwargs)
