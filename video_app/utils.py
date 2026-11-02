"""Helper functions for the HLS files and the cached video list."""

import re
import shutil
import subprocess
from pathlib import Path

from django.conf import settings
from django.core.cache import cache

RESOLUTIONS = {'480p': 480, '720p': 720, '1080p': 1080}
SEGMENT_PATTERN = re.compile(r'^\d{3}\.ts$')
VIDEO_LIST_CACHE_KEY = 'video_list'


def get_hls_dir(video_id, resolution=None):
    """Return the folder of all HLS files of a video or of one resolution."""
    hls_dir = Path(settings.MEDIA_ROOT) / 'hls' / str(video_id)
    return hls_dir / resolution if resolution else hls_dir


def get_hls_file(video_id, resolution, file_name):
    """Return the path of an HLS file if the request is valid, else None."""
    if resolution not in RESOLUTIONS:
        return None
    path = get_hls_dir(video_id, resolution) / file_name
    return path if path.is_file() else None


def is_valid_segment_name(segment):
    """Return True for segment names like '000.ts', which block '../'."""
    return SEGMENT_PATTERN.match(segment) is not None


def build_hls_command(source, output_dir, height):
    """Return the FFmpeg command that converts a video to one HLS stream."""
    return [
        'ffmpeg', '-y', '-i', str(source),
        '-vf', f'scale=-2:{height}',
        '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '23',
        '-c:a', 'aac', '-b:a', '128k',
        '-hls_time', '10', '-hls_playlist_type', 'vod',
        '-hls_segment_filename', str(output_dir / '%03d.ts'),
        str(output_dir / 'index.m3u8'),
    ]


def build_thumbnail_command(source, output_file):
    """Return the FFmpeg command that saves a typical frame as an image."""
    return [
        'ffmpeg', '-y', '-i', str(source),
        '-vf', 'thumbnail,scale=640:-2', '-frames:v', '1',
        str(output_file),
    ]


def run_ffmpeg(command):
    """Run an FFmpeg command and raise an error if it fails."""
    subprocess.run(command, check=True, capture_output=True)


def delete_video_files(video):
    """Delete the original, the thumbnail and all HLS files of a video."""
    if video.video_file:
        video.video_file.delete(save=False)
    if video.thumbnail:
        video.thumbnail.delete(save=False)
    shutil.rmtree(get_hls_dir(video.id), ignore_errors=True)


def clear_video_list_cache():
    """Remove the cached video list so the next request rebuilds it."""
    cache.delete(VIDEO_LIST_CACHE_KEY)
