from django.db import models
from django.utils import timezone
import os

class UploadedFile(models.Model):
    title = models.CharField(max_length=100, blank=True)
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(default=timezone.now)
    
    def save(self, *args, **kwargs):
        if not self.title:
            self.title = os.path.splitext(os.path.basename(self.file.name))[0]
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"File uploaded at {self.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')}"
