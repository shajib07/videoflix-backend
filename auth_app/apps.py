"""App configuration for the authentication app."""

from django.apps import AppConfig


class AuthAppConfig(AppConfig):
    """Configure the app that handles accounts and JWT cookies."""

    name = 'auth_app'
