"""Database models for the videos."""

from django.db import models


class Video(models.Model):
    """A video that is converted to HLS streams in several resolutions."""

    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=100)
    video_file = models.FileField(upload_to='videos/')
    thumbnail = models.FileField(upload_to='thumbnails/', blank=True)
    is_converted = models.BooleanField(default=False, editable=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        """Return the title, shown in the admin panel."""
        return self.title
