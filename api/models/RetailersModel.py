from django.db import models  
from api.models import *
from django.contrib.auth.models import User
    
class retailers(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255, null=True) 
    address = models.ForeignKey(addresses, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.company_name if self.company_name else str(self.id)
