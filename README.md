# Videoflix Backend

Videoflix is a small video streaming platform. Users register with their
email address, activate their account through a confirmation email and then
watch videos in 480p, 720p or 1080p. Uploaded videos are converted to HLS
streams in the background with FFmpeg.

This repository contains the REST API built with Django and Django REST
Framework. The matching frontend is available here:
https://github.com/Developer-Akademie-Backendkurs/project.Videoflix

## Features

- Registration with an activation email; accounts stay inactive until the
  link in the email is opened
- Login, logout and token refresh with JWT in HTTP-only cookies and a token
  blacklist on logout
- Password reset by email; the reset link is valid for 24 hours and can only
  be used once
- Generic error messages that never reveal whether an email is registered
- HTML emails based on the Videoflix design templates
- Video upload through the Django admin panel
- Automatic conversion to HLS in 480p, 720p and 1080p and automatic thumbnail
  creation, both running in the background with Django RQ
- Video list cached in Redis, newest videos first
- Deleting a video also deletes its original file, thumbnail and HLS files

## Tech stack

- Python 3.12, Django, Django REST Framework
- Simple JWT with HTTP-only cookies
- PostgreSQL as database
- Redis as cache and as queue for the background worker (Django RQ)
- FFmpeg for the HLS conversion
- Gunicorn and WhiteNoise
- Docker and Docker Compose

## Requirements

- [Docker Desktop](https://docs.docker.com/get-docker/) with Docker Compose
- [git](https://git-scm.com/downloads)
- An email account with SMTP access to send the activation and password
  reset emails (for Gmail, create an
  [app password](https://myaccount.google.com/apppasswords))

Python, PostgreSQL, Redis and FFmpeg do not need to be installed locally.
Everything runs inside the Docker containers.
