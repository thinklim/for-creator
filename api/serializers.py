import uuid
from blog.models import Blog, Category, Post, Tag
from django.contrib.auth.models import User
from django.utils.text import slugify
from rest_framework import serializers


class PostSerializer(serializers.ModelSerializer):
    blog = serializers.StringRelatedField()
    category = serializers.StringRelatedField()
    tag = serializers.StringRelatedField(many=True)
    user = serializers.StringRelatedField()

    created_date = serializers.DateTimeField(format='%Y-%m-%d %H:%M')
    updated_date =  serializers.DateTimeField(format='%Y-%m-%d %H:%M')

    class Meta:
        model = Post
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        extra_kwargs = {'slug_name': {'required': False}, 'blog': {'required': False}}
        read_only_fields = ('slug_name', 'blog')

    def create(self, validated_data):
        slug_name = get_permalink(validated_data['name'])
        user = self.context['request'].user
        blog = Blog.objects.get(user=user)

        validated_data['slug_name'] = slug_name
        validated_data['blog'] = blog

        return Category.objects.create(**validated_data)


    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.slug_name = get_permalink(instance.name)
        instance.blog = validated_data.get('blog', instance.blog)
        instance.save()

        return instance

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'
        extra_kwargs = {'slug_name': {'required': False}, 'blog': {'required': False}}
        read_only_fields = ('slug_name', 'blog')

    def create(self, validated_data):
        slug_name = get_permalink(validated_data['name'])
        user = self.context['request'].user
        blog = Blog.objects.get(user=user)

        validated_data['slug_name'] = slug_name
        validated_data['blog'] = blog

        return Tag.objects.create(**validated_data)


    def update(self, instance, validated_data):
        user = self.context['request'].user
        instance.name = validated_data.get('name', instance.name)
        instance.slug_name = get_permalink(instance.name)
        instance.blog = Blog.objects.get(user=user)
        instance.save()

        return instance

def get_permalink(text):
    slug = slugify(text, allow_unicode=True)
    last_uid = str(uuid.uuid4()).split('-')[-1]
    permalink = slug + '-' + last_uid

    return permalink
