from django.shortcuts import Http404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from blog.models import Post
from .permissions import IsOwnerOrReadOnly
from .serializers import PostSerializer


class PostList(generics.ListAPIView):
    permission_classes = (IsAuthenticated)

    queryset = Post.objects.all()
    serializer_class = PostSerializer

class PostDetail(generics.RetrieveDestroyAPIView):
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)

    queryset = Post.objects.all()
    serializer_class = PostSerializer
