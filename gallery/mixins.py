"""
Reusable RBAC mixins for gallery views.
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from .models import Album, Photo


class AlbumEditPermissionMixin(LoginRequiredMixin):
    """
    Grants access only to the album owner or staff.
    Expects the URL kwarg 'pk' to be the Album primary key,
    or 'album_pk' when used on Photo views.
    """
    def _get_album(self):
        album_pk = self.kwargs.get('pk') or self.kwargs.get('album_pk')
        return get_object_or_404(Album, pk=album_pk)

    def dispatch(self, request, *args, **kwargs):
        album = self._get_album()
        if not album.user_can_edit(request.user):
            raise PermissionDenied(
                "You don't have permission to modify this album."
            )
        return super().dispatch(request, *args, **kwargs)


class AlbumViewPermissionMixin(LoginRequiredMixin):
    """
    Grants view access to owner, collaborators, staff, or public albums.
    """
    def _get_album(self):
        album_pk = self.kwargs.get('pk') or self.kwargs.get('album_pk')
        return get_object_or_404(Album, pk=album_pk)

    def dispatch(self, request, *args, **kwargs):
        album = self._get_album()
        if not album.user_can_view(request.user):
            raise PermissionDenied("You don't have permission to view this album.")
        return super().dispatch(request, *args, **kwargs)


class PhotoEditPermissionMixin(LoginRequiredMixin):
    """
    Grants edit access only if the user can edit the photo's parent album.
    """
    def dispatch(self, request, *args, **kwargs):
        photo = get_object_or_404(Photo, pk=self.kwargs['pk'])
        if not photo.album.user_can_edit(request.user):
            raise PermissionDenied("You don't have permission to edit this photo.")
        self._photo = photo          # cache so get_object() can reuse
        return super().dispatch(request, *args, **kwargs)
