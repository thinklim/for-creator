from django.urls import path
from .views import BlogView, add_blog


app_name = 'blog'

urlpatterns = [
    path('add', add_blog, name='add'),
    path('', BlogView.as_view(), name='blog'),
]