from django.db import models
from django.contrib.auth.models import User
from api.models import *
# Assuming you are using Django's built-in User model
from api.models.ProductsModel import products


class uploads(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    media_file_url = models.CharField(blank=True, max_length=255)
    media_file_name = models.CharField(max_length=250)
    thumbnail = models.ImageField(
        upload_to='upload-media/', blank=True, null=True)
    product = models.ForeignKey(
        products, on_delete=models.CASCADE, blank=True, null=True)
    media_file_type = models.CharField(max_length=120, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.media_file_name

    class Meta:
        verbose_name_plural = 'upload'
