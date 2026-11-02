"""API views for registration, activation, login and password reset."""

import django_rq
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from auth_app.tasks import send_activation_email, send_password_reset_email
from auth_app.utils import (
    blacklist_refresh_token,
    delete_auth_cookies,
    get_error_response,
    get_login_data,
    get_new_access_token,
    get_registration_data,
    get_user_for_token,
    set_access_cookie,
    set_auth_cookies,
)
from .serializers import PasswordConfirmSerializer, RegistrationSerializer

LOGIN_ERROR = 'Please check your input and try again.'
MISSING_TOKEN_ERROR = 'Refresh token is missing.'
INVALID_TOKEN_ERROR = 'Refresh token is invalid.'
INVALID_LINK_ERROR = 'This password reset link is invalid.'


class PublicAPIView(APIView):
    """Base view for endpoints that work without a logged-in user."""

    permission_classes = [AllowAny]
    authentication_classes = []


class RegistrationView(PublicAPIView):
    """Create an inactive user account and send the activation email."""

    def post(self, request):
        """Validate the data, save the user and queue the email."""
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = default_token_generator.make_token(user)
        django_rq.enqueue(send_activation_email, user.id, token)
        return Response(
            get_registration_data(user, token),
            status=status.HTTP_201_CREATED,
        )


class ActivationView(PublicAPIView):
    """Activate a user account with the link from the activation email."""

    def get(self, request, uidb64, token):
        """Activate the account if the uid and the token are valid."""
        user = get_user_for_token(uidb64, token)
        if user is None:
            return Response(
                {'message': 'Activation failed.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.is_active = True
        user.save(update_fields=['is_active'])
        return Response({'message': 'Account successfully activated.'})


class LoginView(PublicAPIView):
    """Log a user in and set the JWT cookies."""

    def post(self, request):
        """Check the credentials and answer with the user data."""
        user = authenticate(
            username=str(request.data.get('email', '')).lower(),
            password=request.data.get('password'),
        )
        if user is None:
            return get_error_response(LOGIN_ERROR, 401)
        response = Response(get_login_data(user))
        set_auth_cookies(response, RefreshToken.for_user(user))
        return response


class LogoutView(PublicAPIView):
    """Log the user out, blacklist the refresh token and clear the cookies."""

    def post(self, request):
        """Invalidate the refresh token and delete both cookies."""
        raw_refresh_token = request.COOKIES.get('refresh_token')
        if raw_refresh_token is None:
            return get_error_response(MISSING_TOKEN_ERROR, 400)
        blacklist_refresh_token(raw_refresh_token)
        response = Response({
            'detail': 'Logout successful! All tokens will be deleted. '
                      'Refresh token is now invalid.'
        })
        delete_auth_cookies(response)
        return response


class CookieTokenRefreshView(PublicAPIView):
    """Issue a new access token using the refresh token cookie."""

    def post(self, request):
        """Set a new access token cookie if the refresh token is valid."""
        raw_refresh_token = request.COOKIES.get('refresh_token')
        if raw_refresh_token is None:
            return get_error_response(MISSING_TOKEN_ERROR, 400)
        access_token = get_new_access_token(raw_refresh_token)
        if access_token is None:
            return get_error_response(INVALID_TOKEN_ERROR, 401)
        response = Response(
            {'detail': 'Token refreshed', 'access': str(access_token)}
        )
        set_access_cookie(response, access_token)
        return response


class PasswordResetView(PublicAPIView):
    """Send the password reset email without revealing known accounts."""

    def post(self, request):
        """Queue the reset email if an active user has this email."""
        email = str(request.data.get('email', '')).lower()
        user = User.objects.filter(username=email, is_active=True).first()
        if user is not None:
            token = default_token_generator.make_token(user)
            django_rq.enqueue(send_password_reset_email, user.id, token)
        return Response(
            {'detail': 'An email has been sent to reset your password.'}
        )


class PasswordConfirmView(PublicAPIView):
    """Set a new password with the link from the password reset email."""

    def post(self, request, uidb64, token):
        """Save the new password if the link and the passwords are valid."""
        user = get_user_for_token(uidb64, token)
        if user is None:
            return get_error_response(INVALID_LINK_ERROR, 400)
        serializer = PasswordConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user.set_password(serializer.validated_data['new_password'])
        user.save(update_fields=['password'])
        return Response(
            {'detail': 'Your Password has been successfully reset.'}
        )
