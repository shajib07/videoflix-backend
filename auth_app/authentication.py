"""Custom authentication that reads the JWT access token from a cookie."""

from rest_framework_simplejwt.authentication import JWTAuthentication


class CookieJWTAuthentication(JWTAuthentication):
    """Authenticate requests via the HTTP-only 'access_token' cookie."""

    def authenticate(self, request):
        """Return (user, token) for a valid access token cookie, else None."""
        raw_token = request.COOKIES.get('access_token')
        if raw_token is None:
            return None
        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token
