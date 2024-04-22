from django.db import models
from django import forms 

SIZE_CHOICES = (
        ("Small", "Small"),
        ("Medium", "Medium"),
        ("Large", "Large"),
        ("XL", "Extra Large"),
        ("XXL", "Double Extra Large"),
    )

GARMENT_TYPES = (
        ("Headwear", "Headwear"),
        ("Topwear", "Topwear"),
        ("Bottomwear", "Bottomwear"),
        ("Footwear", "Footwear"),
        ("One Piece", "One Piece"),
        ('Accessories','Accessories')
    )
class categories(models.Model):
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=GARMENT_TYPES, default="One Piece")
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name
    
class brand(models.Model):
    name = models.CharField(max_length=25)
    logo = models.URLField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.name + f"({self.id})"
    
    class Meta:
        ordering = ('name',)

class products(models.Model):
    STOCK_CHOICES = (
        ("In stock", "In stock"),
        ("Out of stock", "Out of stock")
    )
    
    title = models.CharField(max_length=255)
    brand = models.ForeignKey(brand, on_delete=models.PROTECT, null=True, blank=True)
    label = models.CharField(max_length=25, null=True, blank=True)
    actual_price = models.IntegerField()
    sold_price = models.IntegerField()
    img_url = models.URLField(max_length=500)
    video = models.FileField(
        upload_to='videos_uploaded/', null=True, blank=True)
    currency = models.CharField(max_length=4)
    color = models.CharField(max_length=20)
    category = models.ForeignKey(
        categories, on_delete=models.PROTECT, null=True, blank=True)
    enable_product = models.BooleanField(default=True)
    stock_status = models.CharField(
        max_length=20, choices=STOCK_CHOICES, default="In stock")
    size_range = models.CharField(
        max_length=20, choices=SIZE_CHOICES, default="Medium")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    deleted_at = models.DateField(null=True, blank=True)
    def __str__(self):
        return self.title + f"({self.id})"

class product_clo_3d(models.Model):
    product = models.ForeignKey(products, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    m_small_s = models.FileField(upload_to='clo_3d/', null=True, blank=True)
    m_small_m = models.FileField(upload_to='clo_3d/', null=True, blank=True)
    m_small_l = models.FileField(upload_to='clo_3d/', null=True, blank=True)
    m_small_xl = models.FileField(upload_to='clo_3d/', null=True, blank=True)
    m_small_xxl = models.FileField(upload_to='clo_3d/', null=True, blank=True)
    m_medium_s = models.FileField(upload_to='clo_3d/', null=True, blank=True)
    m_medium_m = models.FileField(upload_to='clo_3d/', null=True, blank=True)
    m_medium_l = models.FileField(upload_to='clo_3d/', null=True, blank=True)
    m_medium_xl = models.FileField(upload_to='clo_3d/', null=True, blank=True)
    m_medium_xxl = models.FileField(upload_to='clo_3d/', null=True, blank=True)
    m_large_s = models.FileField(upload_to='clo_3d/', null=True, blank=True)
    m_large_m = models.FileField(upload_to='clo_3d/', null=True, blank=True)
    m_large_l = models.FileField(upload_to='clo_3d/', null=True, blank=True)
    m_large_xl = models.FileField(upload_to='clo_3d/', null=True, blank=True)
    m_large_xxl = models.FileField(upload_to='clo_3d/', null=True, blank=True)
    m_xlarge_s = models.FileField(upload_to='clo_3d/', null=True, blank=True)
    m_xlarge_m = models.FileField(upload_to='clo_3d/', null=True, blank=True)
    m_xlarge_l = models.FileField(upload_to='clo_3d/', null=True, blank=True)
    m_xlarge_xl = models.FileField(upload_to='clo_3d/', null=True, blank=True)
    m_xlarge_xxl = models.FileField(upload_to='clo_3d/', null=True, blank=True)
    m_xxlarge_s = models.FileField(upload_to='clo_3d/', null=True, blank=True)
    m_xxlarge_m = models.FileField(upload_to='clo_3d/', null=True, blank=True)
    m_xxlarge_l = models.FileField(upload_to='clo_3d/', null=True, blank=True)
    m_xxlarge_xl = models.FileField(upload_to='clo_3d/', null=True, blank=True)
    m_xxlarge_xxl = models.FileField(upload_to='clo_3d/', null=True, blank=True)

    f_small_s = models.FileField(upload_to='clo_3d/', null=True, blank=True)
    f_small_m = models.FileField(upload_to='clo_3d/', null=True, blank=True)
    f_small_l = models.FileField(upload_to='clo_3d/', null=True, blank=True)
    f_small_xl = models.FileField(upload_to='clo_3d/', null=True, blank=True)
    f_small_xxl = models.FileField(upload_to='clo_3d/', null=True, blank=True)
    f_medium_s = models.FileField(upload_to='clo_3d/', null=True, blank=True)
    f_medium_m = models.FileField(upload_to='clo_3d/', null=True, blank=True)
    f_medium_l = models.FileField(upload_to='clo_3d/', null=True, blank=True)
    f_medium_xl = models.FileField(upload_to='clo_3d/', null=True, blank=True)
    f_medium_xxl = models.FileField(upload_to='clo_3d/', null=True, blank=True)
    f_large_s = models.FileField(upload_to='clo_3d/', null=True, blank=True)
    f_large_m = models.FileField(upload_to='clo_3d/', null=True, blank=True)
    f_large_l = models.FileField(upload_to='clo_3d/', null=True, blank=True)
    f_large_xl = models.FileField(upload_to='clo_3d/', null=True, blank=True)
    f_large_xxl = models.FileField(upload_to='clo_3d/', null=True, blank=True)
    f_xlarge_s = models.FileField(upload_to='clo_3d/', null=True, blank=True)
    f_xlarge_m = models.FileField(upload_to='clo_3d/', null=True, blank=True)
    f_xlarge_l = models.FileField(upload_to='clo_3d/', null=True, blank=True)
    f_xlarge_xl = models.FileField(upload_to='clo_3d/', null=True, blank=True)
    f_xlarge_xxl = models.FileField(upload_to='clo_3d/', null=True, blank=True)
    f_xxlarge_s = models.FileField(upload_to='clo_3d/', null=True, blank=True)
    f_xxlarge_m = models.FileField(upload_to='clo_3d/', null=True, blank=True)
    f_xxlarge_l = models.FileField(upload_to='clo_3d/', null=True, blank=True)
    f_xxlarge_xl = models.FileField(upload_to='clo_3d/', null=True, blank=True)
    f_xxlarge_xxl = models.FileField(upload_to='clo_3d/', null=True, blank=True)
    def __str__(self):
        return self.product.title + f"({self.id})"
    
class background(models.Model):
    title = models.CharField(max_length=255)
    thumbnail = models.URLField(max_length=500, null=True, blank=True)
    model = models.FileField(upload_to='backgrounds/')
    
    def __str__(self):
        return self.title + f"({self.id})"
    
    class Meta:
        ordering = ('id',)