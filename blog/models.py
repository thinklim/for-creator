from django.db import models

#https://docs.djangoproject.com/en/2.2/topics/auth/customizing/#referencing-the-user-model
from django.conf import settings


class Theme(models.Model):
    name = models.CharField(max_length=30, unique=True)
    slug_name = models.SlugField(max_length=50, unique=True, allow_unicode=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Blog(models.Model):
    name = models.CharField(max_length=50, unique=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    theme = models.ForeignKey(Theme, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=30)
    slug_name = models.SlugField(max_length=50, unique=True, allow_unicode=True)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

class Attachment(models.Model):
    name = models.CharField(max_length=30)
    image = models.ImageField(upload_to='blog/%Y/%m/%d')
    created_date = models.DateTimeField(auto_now_add=True)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=30)
    slug_name = models.SlugField(max_length=50, unique=True, allow_unicode=True)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Post(models.Model):
    title = models.CharField(max_length=100, db_index=True)
    content = models.TextField()
    thumbnail = models.ImageField(upload_to='blog/%Y/%m/%d', blank=True) #upload path 문자열이 저장됨.
    slug_title = models.SlugField(max_length=150, unique=True, allow_unicode=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    tag = models.ManyToManyField(Tag, blank=True)

    def __str__(self):
        return self.title
