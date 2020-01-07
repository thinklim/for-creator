from django.db import models

#https://docs.djangoproject.com/en/2.2/topics/auth/customizing/#referencing-the-user-model
from django.conf import settings


class Theme(models.Model):
    name = models.CharField(max_length=30, unique=True)
    slug_name = models.SlugField(max_length=50, unique=True, allow_unicode=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

class Blog(models.Model):
    name = models.CharField(max_length=50, unique=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    theme = models.ForeignKey(Theme, on_delete=models.SET_NULL, null=True)

class Category(models.Model):
    name = models.CharField(max_length=30)
    slug_name = models.SlugField(max_length=50, unique=True, allow_unicode=True)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)

class Attachment(models.Model):
    name = models.CharField(max_length=30)
    resource_type = models.CharField(max_length=100)
    path = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

class Tag(models.Model):
    name = models.CharField(max_length=30)
    slug_name = models.SlugField(max_length=50, unique=True, allow_unicode=True)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)

class Post(models.Model):
    title = models.CharField(max_length=100, db_index=True)
    content = models.TextField()
    image = models.ImageField(upload_to='posts/%Y/%m/%d', blank=True)
    slug_title = models.SlugField(max_length=150, unique=True, allow_unicode=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    attachment = models.ManyToManyField(Attachment)
    tag = models.ManyToManyField(Tag)



