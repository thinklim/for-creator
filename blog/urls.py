from django.urls import register_converter, path
from .views import BlogCreateView, MemberBlogPostDetailView,  MemberBlogView, upload
from .views import MemberBlogSettingView, MemberBlogSettingPostCreateView, MemberBlogSettingPostListView, MemberBlogSettingPostEditView
from .views import MemberBlogSettingCategoryListView, MemberBlogSettingTagListView
from . import converters

app_name = 'blog'

# url 한글 slug 문제 해결
register_converter(converters.UnicodeSlugConverter, 'uslug')

urlpatterns = [
    path('add', BlogCreateView.as_view(), name='add'),
    path('upload', upload, name='upload'),
    path('<str:username>/settings/categories', MemberBlogSettingCategoryListView.as_view(), name='member_blog_setting_category'),
    path('<str:username>/settings/posts/<int:pk>', MemberBlogSettingPostEditView.as_view(), name='member_blog_setting_post_edit'),
    path('<str:username>/settings/posts/new', MemberBlogSettingPostCreateView.as_view(), name='member_blog_setting_post_new'),
    path('<str:username>/settings/posts', MemberBlogSettingPostListView.as_view(), name='member_blog_setting_post'),
    path('<str:username>/settings/tags', MemberBlogSettingTagListView.as_view(), name='member_blog_setting_tag'),
    path('<str:username>/settings', MemberBlogSettingView.as_view(), name='member_blog_setting'),
    path('<str:username>/<uslug:slug_title>', MemberBlogPostDetailView.as_view(), name='member_blog_post_detail'),
    path('<str:username>', MemberBlogView.as_view(), name='member_blog'),
]