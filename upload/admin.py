from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Farmer, UploadedFile

admin.site.register(Farmer, UserAdmin)

@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_at')
    search_fields = ('title',)
    list_filter = ('uploaded_at',)
