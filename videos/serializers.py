from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

from videos.models import Video

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    """

    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    """

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        """
        Creates a new user instance with hashed password and generates a token for the user.

        Args:
            validated_data (dict): Validated data containing username, email, and password.

        Returns:
            User: Created user object.
        """
        user = User.objects.create_user(validated_data['username'], validated_data['email'], validated_data['password'])
        Token.objects.create(user=user)  # Create a token for the user
        return user


class VideoSerializer(serializers.ModelSerializer):
    """
    Serializer for Video model.
    """

    class Meta:
        model = Video
        fields = ['id', 'name', 'url', 'created_at']
