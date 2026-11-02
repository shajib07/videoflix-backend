"""URL routes for the video endpoints."""

from django.urls import path

from .views import HlsManifestView, HlsSegmentView, VideoListView

urlpatterns = [
    path('video/', VideoListView.as_view(), name='video_list'),
    path(
        'video/<int:movie_id>/<str:resolution>/index.m3u8',
        HlsManifestView.as_view(),
        name='video_manifest',
    ),
    path(
        'video/<int:movie_id>/<str:resolution>/<str:segment>/',
        HlsSegmentView.as_view(),
        name='video_segment',
    ),
    # The playlist lists segments as "000.ts", so the player requests them
    # relative to index.m3u8 and without the trailing slash.
    path(
        'video/<int:movie_id>/<str:resolution>/<str:segment>',
        HlsSegmentView.as_view(),
    ),
]
