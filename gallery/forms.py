from django import forms
from .models import Album, Photo


class AlbumForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = ['name', 'description', 'is_public']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Summer Vacation 2025',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional description…',
            }),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['title', 'description', 'image']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Sunset at the beach',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
            }),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }
