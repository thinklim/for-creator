from django.urls import path
from .views import PostDetail, PostList


app_name = 'api'

urlpatterns = [
    path('posts', PostList.as_view()),
    path('posts/<int:pk>', PostDetail.as_view()),
]