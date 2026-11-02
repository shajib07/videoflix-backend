"""Serializers for the video endpoints."""

from rest_framework import serializers

from video_app.models import Video


class VideoSerializer(serializers.ModelSerializer):
    """Return the data the dashboard needs to list a video."""

    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = [
            'id',
            'created_at',
            'title',
            'description',
            'thumbnail_url',
            'category',
        ]

    def get_thumbnail_url(self, video):
        """Return the absolute URL of the thumbnail, or None if missing."""
        if not video.thumbnail:
            return None
        return self.context['request'].build_absolute_uri(video.thumbnail.url)
