"""Background tasks that convert uploaded videos via the RQ worker."""

from django.conf import settings

from .models import Video
from .utils import (
    RESOLUTIONS,
    build_hls_command,
    build_thumbnail_command,
    get_hls_dir,
    run_ffmpeg,
)


def convert_to_hls(video):
    """Create an HLS stream of the video for every resolution."""
    for resolution, height in RESOLUTIONS.items():
        output_dir = get_hls_dir(video.id, resolution)
        output_dir.mkdir(parents=True, exist_ok=True)
        command = build_hls_command(
            video.video_file.path, output_dir, height
        )
        run_ffmpeg(command)


def create_thumbnail(video):
    """Save a frame of the video as its thumbnail if none was uploaded."""
    if video.thumbnail:
        return
    relative_path = f'thumbnails/{video.id}.jpg'
    output_file = settings.MEDIA_ROOT / relative_path
    output_file.parent.mkdir(parents=True, exist_ok=True)
    run_ffmpeg(build_thumbnail_command(video.video_file.path, output_file))
    video.thumbnail.name = relative_path


def convert_video(video_id):
    """Convert a video to HLS, create its thumbnail and mark it as ready."""
    video = Video.objects.get(pk=video_id)
    convert_to_hls(video)
    create_thumbnail(video)
    video.is_converted = True
    video.save(update_fields=['thumbnail', 'is_converted'])
