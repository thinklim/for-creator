from django import forms
from .models import Blog, Category, Post, Tag


class BlogCreateForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ['name', 'theme']

class MemberBlogSettingPostNewCreateForm(forms.ModelForm):
    form_tags = {'title': '제목', 'image': '썸네일', 'category': '카테고리', 'tag': '태그', 'content': '내용'}
    
    def __init__(self, blog, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.blog = blog

        for key, value in form_tags.items():
            self.fields[key].label = value
            self.fields[key].widget.attrs.update({'class': 'form-control'})

            if key == 'category':
                self.fields[key].queryset = Category.objects.filter(blog=self.blog)
            elif key == 'tag':
                self.fields[key].queryset = Tag.objects.filter(blog=self.blog)

    class Meta:
        model = Post
        fields = ['title', 'image', 'category', 'tag', 'content']