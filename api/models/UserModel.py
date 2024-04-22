from django.db import models
from django.contrib.auth.models import User, AbstractUser, UserManager
from django.db.models.query import QuerySet
from django.utils.translation import gettext_lazy as _

class CustomUserManager(UserManager):
    def get_active_users(self, **kwargs):
        # Override the default queryset to exclude deleted users
        return super().get_queryset().filter(is_deleted=False, **kwargs)
    
    def get_deleted(self, **kwargs):
        # Add additional filters to get_deleted
        return super().get_queryset().filter(is_deleted=True, **kwargs)
        

class CustomUser(AbstractUser):
    is_deleted = models.BooleanField(default=False)
    objects = CustomUserManager()
    def soft_delete(self):
        # Perform soft delete by setting is_deleted to True
        self.is_deleted = True
        self.save()
    def __str__(self) -> str:
        return f"{self.username}({self.id})"

class addresses(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)
    country = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.street}, {self.city}, {self.state}, {self.postal_code}"

class UserProfileManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

class user_profile(models.Model):
    GENDER_CHOICES = (
        ("Male", "Male"),
        ("Female", "Female"),
    )
    objects = UserProfileManager()
    gender = models.CharField(
        max_length=20, choices=GENDER_CHOICES, default="Male")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    profile_picture = models.ImageField(
        upload_to='profile-pictures/', blank=True, null=True)
    country_code = models.CharField(max_length=5, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True)
    address = models.ForeignKey(addresses, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    phone_is_verified = models.BooleanField(default=False)
    company_name = models.CharField(max_length=255, null=True, blank=True)
    size = models.CharField(max_length=25, null=True, blank=True)
    class Meta:
        verbose_name_plural = 'user profile'

class user_measurement(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    height = models.FloatField(null=True, blank=True)
    shoulder = models.FloatField(null=True, blank=True)
    back_width = models.FloatField(null=True, blank=True)
    sleeve = models.FloatField(null=True, blank=True)
    waist = models.FloatField(null=True, blank=True)
    chest = models.FloatField(null=True, blank=True)
    neck = models.FloatField(null=True, blank=True)
    waist_to_hip = models.FloatField(null=True, blank=True)
    hip = models.FloatField(null=True, blank=True)
    shoulder_to_waist = models.FloatField(null=True, blank=True)
    front_chest = models.FloatField(null=True, blank=True)
    inside_leg = models.FloatField(null=True, blank=True)
    outside_leg = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class user_feedback(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    overall_experience = models.IntegerField(null=True,blank=True)
    input_feedback = models.CharField(max_length=255, null=True,blank=True)
    scan_feedback = models.IntegerField(null=True,blank=True)
    fit_satisfaction = models.IntegerField(null=True,blank=True)
    app_rating = models.IntegerField(null=True,blank=True)

class OTP(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    otp = models.CharField(max_length=6, null=True)
    created_at = models.DateTimeField(auto_now=True)

class PasswordResetToken(models.Model):
    token = models.CharField(max_length=100)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(null=True, blank=True)
