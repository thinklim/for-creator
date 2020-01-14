from django.urls import path
from .views import BlogView, MemberBlogView, add_blog


app_name = 'blog'

urlpatterns = [
    path('<str:username>', MemberBlogView.as_view(), name='member_blog'),
    path('add/', add_blog, name='add'),
    path('', BlogView.as_view(), name='blog'),
]