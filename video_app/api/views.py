"""API views for the video list and the HLS streaming files."""

from django.core.cache import cache
from django.http import FileResponse, Http404
from rest_framework.response import Response
from rest_framework.views import APIView

from video_app.models import Video
from video_app.utils import (
    VIDEO_LIST_CACHE_KEY,
    get_hls_file,
    is_valid_segment_name,
)
from .serializers import VideoSerializer

VIDEO_LIST_CACHE_TIMEOUT = 60 * 15


class VideoListView(APIView):
    """List all converted videos, newest first, cached in Redis."""

    def get(self, request):
        """Return the cached list or build and cache it."""
        data = cache.get(VIDEO_LIST_CACHE_KEY)
        if data is None:
            videos = Video.objects.filter(is_converted=True)
            context = {'request': request}
            data = VideoSerializer(videos, many=True, context=context).data
            cache.set(VIDEO_LIST_CACHE_KEY, data, VIDEO_LIST_CACHE_TIMEOUT)
        return Response(data)


class HlsManifestView(APIView):
    """Serve the HLS playlist of a video in one resolution."""

    def get(self, request, movie_id, resolution):
        """Return the index.m3u8 file or 404 if it does not exist."""
        path = get_hls_file(movie_id, resolution, 'index.m3u8')
        if path is None:
            raise Http404('Video or manifest not found.')
        return FileResponse(
            open(path, 'rb'), content_type='application/vnd.apple.mpegurl'
        )


class HlsSegmentView(APIView):
    """Serve one HLS video segment of a video in one resolution."""

    def get(self, request, movie_id, resolution, segment):
        """Return the .ts segment or 404 if it does not exist."""
        path = None
        if is_valid_segment_name(segment):
            path = get_hls_file(movie_id, resolution, segment)
        if path is None:
            raise Http404('Video or segment not found.')
        return FileResponse(open(path, 'rb'), content_type='video/MP2T')
