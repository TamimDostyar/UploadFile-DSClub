from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
import os
from django.core.validators import MinValueValidator, MaxValueValidator

class Farmer(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True)
    farm_location = models.CharField(max_length=200, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    days = models.IntegerField(default=7, validators=[MinValueValidator(1), MaxValueValidator(14)])
    
    def __str__(self):
        return self.username

class UploadedFile(models.Model):
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE, related_name='uploads', null=True, blank=True)
    title = models.CharField(max_length=100, blank=True)
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(default=timezone.now)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    location_name = models.CharField(max_length=200, null=True, blank=True)
    prediction = models.CharField(max_length=50, null=True, blank=True)
    confidence = models.FloatField(null=True, blank=True)
    forecast_days = models.IntegerField(default=2, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.title:
            self.title = os.path.splitext(os.path.basename(self.file.name))[0]
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"File uploaded by {self.farmer.username if self.farmer else 'Unknown'} at {self.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')}"
