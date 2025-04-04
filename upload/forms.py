from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import UploadedFile, Farmer

class FarmerRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=15, required=True)
    farm_location = forms.CharField(max_length=200, required=True)
    profile_picture = forms.ImageField(required=False)

    class Meta:
        model = Farmer
        fields = ('username', 'email', 'phone_number', 'farm_location', 'profile_picture', 'password1', 'password2')

class UploadFileForm(forms.ModelForm):
    class Meta:
        model = UploadedFile
        fields = ['file', 'latitude', 'longitude']
        widgets = {
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*' 
            }),
            'latitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': 'any',
                'placeholder': 'Enter latitude'
            }),
            'longitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': 'any',
                'placeholder': 'Enter longitude'
            })
        } 