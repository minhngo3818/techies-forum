from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from .models import Thread, Comment, Like, LikeComment
from .serializers import ThreadSerializers, CommentSerializers, LikeSerializers, LikeCommentSerializers


class ThreadViews(viewsets.ModelViewSet):
    serializer_class = ThreadSerializers
    queryset = Thread.objects.all()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def get_queryset(self):
        user = self.request.user
        return Thread.objects.filter(created_by=user)


class CommentViews(viewsets.ModelViewSet):
    serializer_class = CommentSerializers
    queryset = Comment.objects.all()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def get_queryset(self):
        user = self.request.user
        return Comment.objects.filter(created_by=user)


class LikeViews(viewsets.ModelViewSet):
    serializer_class = LikeSerializers
    queryset = Like.objects.all()

    def get_queryset(self):
        thread = self.request.thread
        return Like.objects.filter(thread=thread)


class LikeCommentViews(viewsets.ModelViewSet):
    serializer_class = LikeCommentSerializers
    query_set = LikeComment.objects.all()

    def get_queryset(self):
        comment = self.request.comment
        return LikeComment.objects.filter(comment=comment)

