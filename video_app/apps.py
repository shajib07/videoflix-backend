"""App configuration for the video app."""

from django.apps import AppConfig


class VideoAppConfig(AppConfig):
    """Configure the app that stores, converts and streams videos."""

    name = 'video_app'

    def ready(self):
        """Connect the signals that convert and clean up the videos."""
        from . import signals  # noqa: F401
