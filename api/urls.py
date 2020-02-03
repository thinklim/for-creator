from django.urls import path
from .views import CategoryList, CategoryDetail, ThemePostList, PostDetail, TagDetail, TagList


app_name = 'api'

urlpatterns = [
    path('categories', CategoryList.as_view()),
    path('categories/<int:pk>', CategoryDetail.as_view()),
    path('themes/<str:theme_slug_name>/posts', ThemePostList.as_view()),
    path('posts/<int:pk>', PostDetail.as_view()),
    path('tags', TagList.as_view()),
    path('tags/<int:pk>', TagDetail.as_view()),
]