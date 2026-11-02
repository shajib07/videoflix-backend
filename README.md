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

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/shajib07/videoflix-backend.git
   cd videoflix-backend
   ```

2. Create the `.env` file from the template:

   ```bash
   cp .env.template .env
   ```

3. Open `.env` and fill in at least the database and email values (see
   [Environment variables](#environment-variables)). Set the database values
   before the first start, because the database container is created with
   them.

4. Make sure Docker Desktop is running, then build and start the project:

   ```bash
   docker compose up --build
   ```

   If this does not work, use `docker-compose up --build` instead.

The start script waits for PostgreSQL, runs the migrations, collects the
static files, creates the superuser from the `.env` file and starts the RQ
worker and the Gunicorn server.

The API is now available at http://127.0.0.1:8000/api/ and the admin panel
at http://127.0.0.1:8000/admin/.

> **Note for Windows:** `backend.entrypoint.sh` must be saved with LF line
> endings, otherwise the container stops with
> `exec ./backend.entrypoint.sh: no such file or directory`.

## Environment variables

All variables are read from the `.env` file. Do not rename or delete the
variables from the template.

| Variable | Description |
| :--- | :--- |
| `DJANGO_SUPERUSER_USERNAME` | Username of the admin account created on start |
| `DJANGO_SUPERUSER_PASSWORD` | Password of the admin account |
| `DJANGO_SUPERUSER_EMAIL` | Email of the admin account |
| `SECRET_KEY` | Django secret key, use a long random value |
| `DEBUG` | `True` for development, `False` in production |
| `ALLOWED_HOSTS` | Comma-separated hosts this backend may serve |
| `CSRF_TRUSTED_ORIGINS` | Comma-separated frontend origins, also used as allowed CORS origins |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD` | Name, user and password of the PostgreSQL database |
| `DB_HOST`, `DB_PORT` | Database host and port, `db` and `5432` in Docker |
| `REDIS_HOST`, `REDIS_PORT`, `REDIS_DB` | Redis connection of the RQ worker |
| `REDIS_LOCATION` | Redis URL of the cache |
| `EMAIL_HOST`, `EMAIL_PORT` | SMTP server, e.g. `smtp.gmail.com` and `587` |
| `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` | Login of the email account |
| `EMAIL_USE_TLS`, `EMAIL_USE_SSL` | Use `True`/`False` for port 587, `False`/`True` for port 465 |
| `DEFAULT_FROM_EMAIL` | Sender address of the emails |
| `FRONTEND_URL` | Address of the frontend; the links in the emails point to it. Default: `http://127.0.0.1:5500` |
