from django.shortcuts import Http404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from blog.models import Blog, Category, Post, Tag, Theme
from .permissions import IsOwnerOrReadOnly
from .serializers import CategorySerializer, PostSerializer, TagSerializer


class ThemePostList(generics.ListAPIView):
    serializer_class = PostSerializer

    def get_queryset(self):
        theme_slug_name = self.kwargs['theme_slug_name']
        theme = Theme.objects.get(slug_name=theme_slug_name)
        blog = Blog.objects.filter(theme=theme)
        
        return Post.objects.filter(blog__in=blog).distinct()


class PostDetail(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)

    queryset = Post.objects.all()
    serializer_class = PostSerializer

class CategoryList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)

    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class CategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)

    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class TagDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)

    queryset = Tag.objects.all()
    serializer_class = TagSerializer

class TagList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
        
