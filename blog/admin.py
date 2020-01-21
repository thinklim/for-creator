from django.contrib import admin
from . models import Attachment, Blog, Category, Post, Tag, Theme


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    pass

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',  'created_date', 'updated_date', 'user', 'theme')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug_name': ('name', )}

    list_display = ('id', 'name', 'slug_name')

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug_title': ('title', )}

    list_display = ('id', 'title', 'slug_title', 'created_date', 'updated_date', 'category', 'thumbnail', 'blog', 'user')

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug_name': ('name', )}

    list_display = ('id', 'name', 'slug_name')

@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug_name': ('name', )}

    list_display = ('id', 'name', 'slug_name',  'created_date', 'updated_date')