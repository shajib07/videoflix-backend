"""Admin panel configuration for uploading and managing videos."""

from django.contrib import admin

from .models import Video


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    """Upload videos and see whether their conversion has finished."""

    list_display = ['title', 'category', 'created_at', 'is_converted']
    list_filter = ['category', 'is_converted']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'is_converted']
