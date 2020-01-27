from django.urls import register_converter, path
from .views import add_blog, BlogView, MemberBlogPostDetailView,  MemberBlogView, upload
from .views import MemberBlogSettingView, MemberBlogSettingPostNewCreateView, MemberBlogSettingPostListView, MemberBlogSettingPostEditView
from . views import MemberBlogSettingCategoryListView
from . import converters

app_name = 'blog'

# url 한글 slug 문제 해결
register_converter(converters.BlogPostSlugConverter, 'bslug')

urlpatterns = [
    path('upload', upload, name='upload'),
    path('<str:username>/settings/categories', MemberBlogSettingCategoryListView.as_view(), name='member_blog_setting_category'),
    path('<str:username>/settings/posts/<int:pk>', MemberBlogSettingPostEditView.as_view(), name='member_blog_setting_post_edit'),
    path('<str:username>/settings/posts/new', MemberBlogSettingPostNewCreateView.as_view(), name='member_blog_setting_post_new'),
    path('<str:username>/settings/posts', MemberBlogSettingPostListView.as_view(), name='member_blog_setting_post'),
    path('<str:username>/settings', MemberBlogSettingView.as_view(), name='member_blog_setting'),
    path('<str:username>/<bslug:slug_title>', MemberBlogPostDetailView.as_view(), name='member_blog_post_detail'),
    path('<str:username>', MemberBlogView.as_view(), name='member_blog'),
    path('add/', add_blog, name='add'),
    path('', BlogView.as_view(), name='blog'),
]