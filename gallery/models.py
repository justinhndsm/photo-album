from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField


class Album(models.Model):
    """
    A named collection of photos owned by a user.
    The owner has full admin rights; others get read-only access.
    """
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='owned_albums'
    )
    collaborators = models.ManyToManyField(
        User, blank=True, related_name='shared_albums'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(
        default=False,
        help_text="Public albums are visible to all logged-in users."
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def user_can_edit(self, user):
        """Returns True if this user may add/edit/delete photos in the album."""
        return user.is_staff or self.owner == user

    def user_can_view(self, user):
        """Returns True if this user may view the album."""
        if not user.is_authenticated:
            return False
        return (
            self.is_public
            or self.owner == user
            or self.collaborators.filter(pk=user.pk).exists()
            or user.is_staff
        )


class Photo(models.Model):
    """A single photo belonging to an album."""
    album = models.ForeignKey(
        Album, on_delete=models.CASCADE, related_name='photos'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image = CloudinaryField('image')
    uploaded_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='photos'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.title} ({self.album.name})"
