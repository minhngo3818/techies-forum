from django.shortcuts import render
from django.utils import timezone
from rest_framework import viewsets, generics
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
    IsAdminUser,
    AllowAny,
)
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import User, Profile
from .serializers import (
    CustomTokenObtainPairSerializer,
    UserSerializer,
    UserRegisterSerializer,
    ChangePasswordSerializer,
    ProfileSerializer,
)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom pair view for jwt user authentication
    """

    serializer_class = CustomTokenObtainPairSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Provide ready-only api view user information for admin
    """

    permission_classes = [IsAdminUser]
    queryset = User.objects.all().order_by("-id")
    serializer_class = UserSerializer


class UserRegisterView(generics.CreateAPIView):
    """
    Fetch to create user and add to database
    Response with jwt token pair
    """

    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer


class ChangePasswordView(generics.UpdateAPIView):
    """
    Fetch to update user password
    """

    queryset = User.objects.all()
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]


class ProfileViewSet(viewsets.ModelViewSet):
    """
    Fetch database to read, create, update, and delete profile
    """

    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_date=timezone.now(), owner=self.request.user)
