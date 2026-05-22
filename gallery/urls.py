from django.urls import path
from . import views

urlpatterns = [
    # ── Auth ──────────────────────────────────────────────────────
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/',    views.LoginView.as_view(),    name='login'),
    path('logout/',   views.LogoutView.as_view(),   name='logout'),

    # ── Albums ────────────────────────────────────────────────────
    path('',                              views.AlbumListView.as_view(),   name='album_list'),
    path('albums/new/',                   views.AlbumCreateView.as_view(), name='album_create'),
    path('albums/<int:pk>/',              views.AlbumDetailView.as_view(), name='album_detail'),
    path('albums/<int:pk>/edit/',         views.AlbumUpdateView.as_view(), name='album_update'),
    path('albums/<int:pk>/delete/',       views.AlbumDeleteView.as_view(), name='album_delete'),

    # ── Photos ────────────────────────────────────────────────────
    path('albums/<int:album_pk>/photos/upload/', views.PhotoCreateView.as_view(), name='photo_create'),
    path('photos/<int:pk>/edit/',                views.PhotoUpdateView.as_view(), name='photo_update'),
    path('photos/<int:pk>/delete/',              views.PhotoDeleteView.as_view(), name='photo_delete'),
]
