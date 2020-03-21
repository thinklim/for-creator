from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from .models import Attachment, Blog, Category, Post, Tag


class BlogCreateForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ['name', 'theme']

class MemberBlogSettingPostCreateAndEditForm(forms.ModelForm):
    form_tags = {'title': '제목', 'thumbnail': '썸네일', 'category': '카테고리', 'tag': '태그', 'content': '내용'}
    tag = forms.CharField(max_length=100, required=False)
    content = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = Post
        fields = ['title', 'thumbnail', 'category', 'tag', 'content']
    
    def __init__(self, blog, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for key, value in self.form_tags.items():
            self.fields[key].label = value
            self.fields[key].widget.attrs.update({'class': 'form-control'})

            if key == 'category':
                self.fields[key].queryset = Category.objects.filter(blog=blog)
            elif key == 'tag':
                self.fields[key].widget.attrs.update({'data-role': 'tagsinput'})

class UploadImageFileForm(forms.Form):
    image = forms.ImageField()

class CustomPasswordChangeForm(PasswordChangeForm):
    form_tags = {'old_password': '이전 비밀번호', 'new_password1': '새 비밀번호', 'new_password2': '새 비밀번호 확인'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for key, value in self.form_tags.items():
            self.fields[key].label = value
            self.fields[key].widget.attrs.update({'class': 'form-control'})