# Creator: Tamim Dostyar

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from .models import UploadedFile
from .forms import UploadFileForm
from .ml_processor import ImageProcessor
import os

def home(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.save()
            
            # Process the image using our ML processor
            processor = ImageProcessor()
            result = processor.process_image(file.file.path)
            
            messages.success(request, 'File uploaded successfully! Once ML processing is connected, this image will be automatically analyzed.')
            return JsonResponse({
                'status': result['status'],
                'message': result['message'],
                'redirect_url': '/',
                'processed_info': result['results']
            })
    else:
        form = UploadFileForm()
    
    files = UploadedFile.objects.all().order_by('-uploaded_at')
    return render(request, 'upload/home.html', {'form': form, 'files': files})

def delete_file(request, file_id):
    file = get_object_or_404(UploadedFile, id=file_id)
    if file.file:
        if os.path.exists(file.file.path):
            os.remove(file.file.path)
    file.delete()
    messages.success(request, 'File deleted successfully!')
    return redirect('home')
