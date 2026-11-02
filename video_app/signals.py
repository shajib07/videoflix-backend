"""Signals that start the conversion and clean up the video files."""

import django_rq
from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Video
from .tasks import convert_video
from .utils import clear_video_list_cache, delete_video_files

CONVERSION_TIMEOUT = 60 * 60


def enqueue_conversion(video_id):
    """Queue the conversion of a video in the background worker."""
    django_rq.get_queue('default').enqueue(
        convert_video, video_id, job_timeout=CONVERSION_TIMEOUT
    )


@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    """Start the conversion of new videos and refresh the cached list."""
    clear_video_list_cache()
    if created:
        transaction.on_commit(lambda: enqueue_conversion(instance.id))


@receiver(post_delete, sender=Video)
def video_post_delete(sender, instance, **kwargs):
    """Delete all files of a removed video and refresh the cached list."""
    clear_video_list_cache()
    delete_video_files(instance)
