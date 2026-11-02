"""Serializers for the authentication endpoints."""

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

GENERIC_ERROR = 'Please check your input and try again.'


class RegistrationSerializer(serializers.ModelSerializer):
    """Validate registration data and create a new, inactive user."""

    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'confirmed_password']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True, 'allow_blank': False},
        }

    def validate_email(self, value):
        """Reject a used email without revealing that it is registered."""
        email = value.lower()
        if User.objects.filter(username=email).exists():
            raise serializers.ValidationError(GENERIC_ERROR)
        return email

    def validate(self, data):
        """Ensure both passwords match and the password is strong enough."""
        if data['password'] != data['confirmed_password']:
            raise serializers.ValidationError(
                {'confirmed_password': 'Passwords do not match.'}
            )
        validate_password(data['password'])
        return data

    def create(self, validated_data):
        """Create the user with the email as username, not yet active."""
        return User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            is_active=False,
        )


class PasswordConfirmSerializer(serializers.Serializer):
    """Validate the new password of a password reset."""

    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        """Ensure both passwords match and the password is strong enough."""
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError(
                {'confirm_password': 'Passwords do not match.'}
            )
        validate_password(data['new_password'])
        return data
