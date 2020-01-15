from django.views.generic import DetailView, ListView, TemplateView
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.models import Group, User
from django.db import transaction
from django.http import Http404
from .models import Blog, Category, Theme, Post, Tag
from .forms import BlogCreateForm

class BlogView(TemplateView):
    template_name = 'blog/blog.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['theme_list'] = Theme.objects.all()

        return context

def add_blog(request):
    if request.method == 'POST':
        form = BlogCreateForm(request.POST)

        if form.is_valid():
            blog_create_input_data = form.cleaned_data

            with transaction.atomic():
                blog = Blog(name=blog_create_input_data['name'], theme=blog_create_input_data['theme'], user=request.user)
                blog.save()
                
                blogger_group = Group.objects.get(name='Blogger')
                blogger_group.user_set.add(request.user)
                
                member_group = Group.objects.get(name='Member')
                request.user.groups.remove(member_group)

            return redirect('/blog')
    else:
        form = BlogCreateForm()

    return render(request, 'blog/blog.html')

# def member_blog_view(request, username):
#     if request.method == 'GET':
#         user = get_object_or_404(User, username=username)
#         post_list = Post.objects.filter(user=user)
#         context = {'post_list': post_list}

#         return render(request, 'blog/member_blog.html', context)

class MemberBlogView(ListView):
    template_name = 'blog/member_blog.html'

    def get_queryset(self):
        self.user = get_object_or_404(User, username=self.kwargs['username'])

        return Post.objects.filter(user=self.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.blog = Blog.objects.get(user=self.user)
        context['blog'] = self.blog
        context['categories'] = Category.objects.filter(blog=self.blog)
        context['tags'] = Tag.objects.filter(blog=self.blog)
        context['username'] = self.kwargs['username']

        return context

class MemberBlogPostDetailView(DetailView):
    template_name = 'blog/member_blog_post_detail.html'
    model = Post
    slug_field = 'slug_title'
    slug_url_kwarg = 'slug_title'

    def get_queryset(self):
        self.user = get_object_or_404(User, username=self.kwargs['username'])

        return Post.objects.filter(user=self.user)

class MemberBlogSettingView(TemplateView):
    template_name = 'blog/member_blog_setting.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.username != context['username']:
            raise Http404

        self.blog = get_object_or_404(Blog, user=self.request.user)
        
        return context
