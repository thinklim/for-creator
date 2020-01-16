from django.urls import register_converter, path
from .views import add_blog, BlogView, MemberBlogPostDetailView, MemberBlogSettingView, MemberBlogView
from . import converters

app_name = 'blog'

# url 한글 slug 문제 해결
register_converter(converters.BlogPostSlugConverter, 'bslug')

urlpatterns = [
    path('<str:username>/settings', MemberBlogSettingView.as_view(), name='member_blog_setting'),
    path('<str:username>/<bslug:slug_title>', MemberBlogPostDetailView.as_view(), name='member_blog_post_detail'),
    path('<str:username>', MemberBlogView.as_view(), name='member_blog'),
    path('add/', add_blog, name='add'),
    path('', BlogView.as_view(), name='blog'),
]