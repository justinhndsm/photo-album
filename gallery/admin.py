from django.contrib import admin
from .models import Album, Photo


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display  = ('name', 'owner', 'is_public', 'created_at')
    list_filter   = ('is_public',)
    search_fields = ('name', 'owner__username')
    filter_horizontal = ('collaborators',)


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display  = ('title', 'album', 'uploaded_by', 'uploaded_at')
    list_filter   = ('album',)
    search_fields = ('title', 'album__name', 'uploaded_by__username')
