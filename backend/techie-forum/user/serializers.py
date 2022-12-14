from abc import ABC

from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.db.models import Count
from django.utils.encoding import (
    force_str,
)
from django.utils.http import urlsafe_base64_decode
from rest_framework import exceptions, serializers
from rest_framework.validators import UniqueValidator
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from utils.dynamic_field_serializer import DynamicFieldsModelSerializer
from .models import User, Profile, Project
from forum.models import Thread, Comment, BasePost


class UserSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for viewing user information
    """

    class Meta:
        model = User
        fields = ["id", "username", "email"]


class ProfileSerializer(DynamicFieldsModelSerializer):
    """
    Serialize all related information of user profile
    """

    thread_counts = serializers.SerializerMethodField("get_thread_counts")
    comment_counts = serializers.SerializerMethodField("get_comment_counts")
    like_counts = serializers.SerializerMethodField("get_like_counts")

    class Meta:
        model = Profile
        fields = [
            "id",
            "profile_name",
            "about",
            "avatar",
            "twitter_url",
            "reddit_url",
            "github_url",
            "stackoverflow_url",
            "linkedin_url",
            "indeed_url",
            "thread_counts",
            "comment_counts",
            "like_counts",
        ]

    @classmethod
    def get_thread_counts(cls, profile):
        return Thread.objects.filter(owner=profile.id).count()

    @classmethod
    def get_comment_counts(cls, profile):
        return Comment.objects.filter(owner=profile.id).count()

    @classmethod
    def get_like_counts(cls, profile):
        return BasePost.objects.filter(owner=profile.id).annotate(Count("liked"))


class ProjectSerializer(serializers.ModelSerializer):
    """
    Serialize project information and its owner
    """

    owner = ProfileSerializer(read_only=True, fields=["id", "profile_name"])

    class Meta:
        model = Project
        fields = ["id", "owner", "title", "summary", "demo", "repo"]


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration, return form input with auth tokens
    """

    email = serializers.EmailField(
        required=True, validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        min_length=8,
        max_length=255,
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())],
    )
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)
    tokens = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["email", "username", "password", "password2", "tokens"]
        read_only_fields = ["tokens"]

    def validate(self, attrs):
        if User.objects.filter(username=attrs["username"]).exists():
            raise serializers.ValidationError("Username is already existed!")

        if User.objects.filter(username=attrs["email"]).exists():
            raise serializers.ValidationError("Email is already existed!")

        if not attrs["username"].isalnum():
            raise serializers.ValidationError("Username cannot have special characters")

        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Password didn't match!"})

        # add all fields to create an instance
        return attrs

    @classmethod
    def get_tokens(cls, user):
        # Return generated tokens after successful registering account

        token = RefreshToken.for_user(user=user)
        refresh = str(token)
        access = str(token.access_token)
        return {"refresh": refresh, "access": access}

    def create(self, validate_data):
        return User.objects.create_user(**validate_data)


class LoginSerializer(serializers.ModelSerializer):
    """
    Serializer for log-in, return auth tokens
    """

    username = serializers.CharField(max_length=255, write_only=True, required=True)
    password = serializers.CharField(max_length=128, write_only=True, required=True)
    tokens = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["username", "password", "tokens"]

    @classmethod
    def get_tokens(cls, attrs):
        # Return a token pair in response when calling serializer

        user = User.objects.get(username=attrs["username"])
        refresh = user.get_tokens["refresh"]
        access = user.get_tokens["access"]
        return {"refresh": refresh, "access": access}

    def validate(self, attrs):
        # Validate login input and return user object if succeed

        username = attrs["username"]
        password = attrs["password"]
        user = authenticate(username=username, password=password)

        if username is None:
            raise AuthenticationFailed("Username is required")

        if password is None:
            raise AuthenticationFailed("Password is required")

        if user is None:
            raise AuthenticationFailed("User with username and password does not exist")

        if not user.is_active:
            raise AuthenticationFailed("User is not active")

        if not user.is_verified:
            raise AuthenticationFailed("Email has not been verified")

        return super().validate(attrs)


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer to change password while user is authenticated
    """

    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)
    new_password2 = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        if not self.context["request"].user.check_password(attrs["old_password"]):
            raise serializers.ValidationError("old password is incorrect")

        if attrs["new_password"] != attrs["new_password2"]:
            raise serializers.ValidationError("new password did not match")

        return attrs

    def update(self, instance, validated_data):
        instance.set_password(validated_data["new_password"])
        instance.save()
        return instance


class EmailVerificationSerializer(serializers.ModelSerializer):
    """
    Serializer to verify user email by send a notification
    """

    token = serializers.CharField(max_length=600)

    class Meta:
        model = User
        fields = ["token"]


class RequestResetPasswordSerializer(serializers.Serializer):
    """
    Serializer to send reset password request to user email
    """

    email = serializers.EmailField(min_length=8, required=True)

    # Frontend send user email along with reset password route
    redirect_url = serializers.CharField(max_length=500, required=False)

    class Meta:
        fields = ["email"]

    def validate(self, attrs):
        if not User.objects.filter(email=attrs["email"]).exists():
            raise ValueError("email does not exist")

        return attrs


class ResetPasswordSerializer(serializers.Serializer):
    """
    Serializer to reset password with via attached link
    """

    password = serializers.CharField(
        min_length=8, max_length=255, write_only=True, required=True
    )
    password2 = serializers.CharField(
        min_length=8, max_length=255, write_only=True, required=True
    )
    token = serializers.CharField(min_length=8, max_length=255)
    uidb64 = serializers.CharField(min_length=8)

    class Meta:
        fields = ["password", "password2", "token", "uidb64"]

    def validate(self, attrs):
        # Validate two password fields and
        # decode reset password url uidb64 into id to verify user

        password = attrs["password"]
        password2 = attrs["password2"]
        token = attrs["token"]
        uidb64 = attrs["uidb64"]

        user_id = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(id=user_id)

        if password != password2:
            raise serializers.ValidationError("new password did not match")

        if not PasswordResetTokenGenerator().check_token(user, token):
            raise exceptions.AuthenticationFailed("Reset password url is invalid", 401)

        user.set_password(password)
        user.save()

        return super().validate(attrs)
