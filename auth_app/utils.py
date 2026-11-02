"""Helper functions for accounts, email links and JWT cookies."""

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken


def get_cookie_settings():
    """Return the shared security settings for the auth cookies."""
    return {'httponly': True, 'secure': not settings.DEBUG, 'samesite': 'Lax'}


def set_access_cookie(response, access_token):
    """Attach the access token to the response as an HTTP-only cookie."""
    response.set_cookie(
        'access_token', str(access_token), **get_cookie_settings()
    )


def set_auth_cookies(response, refresh_token):
    """Attach the access and the refresh token as HTTP-only cookies."""
    set_access_cookie(response, refresh_token.access_token)
    response.set_cookie(
        'refresh_token', str(refresh_token), **get_cookie_settings()
    )


def delete_auth_cookies(response):
    """Remove both token cookies from the client."""
    response.delete_cookie('access_token', samesite='Lax')
    response.delete_cookie('refresh_token', samesite='Lax')


def get_new_access_token(raw_refresh_token):
    """Return a new access token for a valid refresh token, otherwise None."""
    try:
        return RefreshToken(raw_refresh_token).access_token
    except TokenError:
        return None


def blacklist_refresh_token(raw_refresh_token):
    """Blacklist the refresh token so it can no longer be used."""
    try:
        RefreshToken(raw_refresh_token).blacklist()
    except TokenError:
        pass


def encode_user_id(user):
    """Return the user id as a URL-safe base64 string."""
    return urlsafe_base64_encode(force_bytes(user.pk))


def get_user_from_uid(uidb64):
    """Return the user for a base64 encoded id, otherwise None."""
    try:
        user_id = force_str(urlsafe_base64_decode(uidb64))
        return User.objects.get(pk=user_id)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return None


def get_user_for_token(uidb64, token):
    """Return the user if the uid and the token belong together, else None."""
    user = get_user_from_uid(uidb64)
    if user is None or not default_token_generator.check_token(user, token):
        return None
    return user


def build_frontend_link(page, user, token):
    """Return the link to a frontend page with the uid and token attached."""
    uid = encode_user_id(user)
    return f'{settings.FRONTEND_URL}/{page}?uid={uid}&token={token}'


def get_registration_data(user, token):
    """Return the response body for a successful registration."""
    return {'user': {'id': user.id, 'email': user.email}, 'token': token}


def get_login_data(user):
    """Return the response body for a successful login."""
    return {
        'detail': 'Login successful',
        'user': {'id': user.id, 'username': user.username},
    }


def get_error_response(detail, status_code):
    """Return an error response with a detail message."""
    return Response({'detail': detail}, status=status_code)
