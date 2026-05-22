"""
Class-Based Views for the Photo Album Management System.

RBAC rules
----------
- Unauthenticated users  → redirected to login for everything
- Authenticated users    → can create albums; view own + public + shared albums
- Album owner / staff    → full CRUD on that album and its photos
- Non-owner              → read-only; raises 403 on any mutation attempt
"""
import cloudinary.uploader
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView,
)

from .forms import AlbumForm, PhotoForm
from .mixins import AlbumEditPermissionMixin, AlbumViewPermissionMixin, PhotoEditPermissionMixin
from .models import Album, Photo


# ─────────────────────────────────────────────────────────────
# Auth Views
# ─────────────────────────────────────────────────────────────

class RegisterView(View):
    template_name = 'gallery/auth/register.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('album_list')
        return render(request, self.template_name, {'form': UserCreationForm()})

    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome, {user.username}! Your account has been created.")
            return redirect('album_list')
        return render(request, self.template_name, {'form': form})


class LoginView(View):
    template_name = 'gallery/auth/login.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('album_list')
        return render(request, self.template_name, {'form': AuthenticationForm()})

    def post(self, request):
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, f"Welcome back, {form.get_user().username}!")
            return redirect(request.GET.get('next', 'album_list'))
        return render(request, self.template_name, {'form': form})


class LogoutView(LoginRequiredMixin, View):
    def post(self, request):
        logout(request)
        messages.info(request, "You have been logged out.")
        return redirect('login')


# ─────────────────────────────────────────────────────────────
# Album Views
# ─────────────────────────────────────────────────────────────

class AlbumListView(LoginRequiredMixin, ListView):
    """
    Shows albums the current user owns or can view (public / shared).
    Staff see all albums.
    """
    template_name = 'gallery/album/list.html'
    context_object_name = 'albums'
    paginate_by = 12

    def get_queryset(self):
        user = self.request.user
        query = self.request.GET.get('q', '')

        if user.is_staff:
            qs = Album.objects.all()
        else:
            qs = Album.objects.filter(
                Q(owner=user) | Q(is_public=True) | Q(collaborators=user)
            ).distinct()

        if query:
            qs = qs.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )
        return qs.order_by('-created_at')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['query'] = self.request.GET.get('q', '')
        return ctx


class AlbumCreateView(LoginRequiredMixin, CreateView):
    model = Album
    form_class = AlbumForm
    template_name = 'gallery/album/form.html'
    success_url = reverse_lazy('album_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, f"Album '{form.instance.name}' created!")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['action'] = 'Create'
        return ctx


class AlbumDetailView(AlbumViewPermissionMixin, DetailView):
    model = Album
    template_name = 'gallery/album/detail.html'
    context_object_name = 'album'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        album = self.object
        query = self.request.GET.get('q', '')
        photo_qs = album.photos.all()
        if query:
            photo_qs = photo_qs.filter(
                Q(title__icontains=query) | Q(description__icontains=query)
            )
        paginator = Paginator(photo_qs, 12)
        ctx['photos'] = paginator.get_page(self.request.GET.get('page'))
        ctx['query'] = query
        ctx['can_edit'] = album.user_can_edit(self.request.user)
        ctx['upload_form'] = PhotoForm()
        return ctx


class AlbumUpdateView(AlbumEditPermissionMixin, UpdateView):
    model = Album
    form_class = AlbumForm
    template_name = 'gallery/album/form.html'

    def get_success_url(self):
        return reverse_lazy('album_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, f"Album '{form.instance.name}' updated!")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['action'] = 'Update'
        return ctx


class AlbumDeleteView(AlbumEditPermissionMixin, DeleteView):
    model = Album
    template_name = 'gallery/album/confirm_delete.html'
    success_url = reverse_lazy('album_list')
    context_object_name = 'album'

    def form_valid(self, form):
        # Delete all Cloudinary assets before removing DB record
        for photo in self.object.photos.all():
            if photo.image:
                try:
                    cloudinary.uploader.destroy(photo.image.public_id)
                except Exception as e:
                    print(f"Cloudinary deletion warning: {e}")
        name = self.object.name
        response = super().form_valid(form)
        messages.success(self.request, f"Album '{name}' and all its photos have been deleted.")
        return response


# ─────────────────────────────────────────────────────────────
# Photo Views
# ─────────────────────────────────────────────────────────────

class PhotoCreateView(AlbumEditPermissionMixin, CreateView):
    """Upload a photo into an album. album_pk comes from the URL."""
    model = Photo
    form_class = PhotoForm
    template_name = 'gallery/photo/form.html'

    def _get_album(self):
        return get_object_or_404(Album, pk=self.kwargs['album_pk'])

    def form_valid(self, form):
        form.instance.album = self._get_album()
        form.instance.uploaded_by = self.request.user
        messages.success(self.request, f"Photo '{form.instance.title}' uploaded!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('album_detail', kwargs={'pk': self.kwargs['album_pk']})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['action'] = 'Upload'
        ctx['album'] = self._get_album()
        return ctx


class PhotoUpdateView(PhotoEditPermissionMixin, UpdateView):
    model = Photo
    form_class = PhotoForm
    template_name = 'gallery/photo/form.html'

    def get_object(self):
        return self._photo  # set by mixin

    def form_valid(self, form):
        messages.success(self.request, f"Photo '{form.instance.title}' updated!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('album_detail', kwargs={'pk': self.object.album.pk})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['action'] = 'Edit'
        ctx['album'] = self.object.album
        return ctx


class PhotoDeleteView(PhotoEditPermissionMixin, DeleteView):
    model = Photo
    template_name = 'gallery/photo/confirm_delete.html'
    context_object_name = 'photo'

    def get_object(self):
        return self._photo

    def form_valid(self, form):
        photo = self.object
        album_pk = photo.album.pk
        if photo.image:
            try:
                cloudinary.uploader.destroy(photo.image.public_id)
            except Exception as e:
                print(f"Cloudinary deletion warning: {e}")
        title = photo.title
        response = super().form_valid(form)
        messages.success(self.request, f"'{title}' was permanently deleted.")
        return response

    def get_success_url(self):
        return reverse_lazy('album_detail', kwargs={'pk': self.object.album.pk})
