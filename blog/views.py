import uuid
from django.views.generic import CreateView, DetailView, ListView, TemplateView
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.models import Group, User
from django.db import transaction
from django.http import Http404
from django.utils.text import slugify
from .models import Blog, Category, Theme, Post, Tag
from .forms import BlogCreateForm, MemberBlogSettingPostNewCreateForm

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

class MemberBlogSettingPostListView(ListView):
    template_name = 'blog/member_blog_setting_post.html'

    def get_queryset(self, **kwargs):
        username = self.kwargs['username']

        if self.request.user.username != username:
            raise Http404

        self.blog = get_object_or_404(Blog, user=self.request.user)

        return Post.objects.filter(blog=self.blog).order_by('-id')

class MemberBlogSettingPostNewCreateView(CreateView):
    template_name = 'blog/member_blog_setting_post_new.html'

    def get(self, request, *args, **kwargs):
        context = {'form': MemberBlogSettingPostNewCreateForm(self._get_blog(request))}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        blog = self._get_blog(request)
        form = MemberBlogSettingPostNewCreateForm(blog, request.POST, request.FILES)

        if form.is_valid():
            new_post = form.save(commit=False)

            slug_title = slugify(new_post.title, allow_unicode=True)
            last_uid = str(uuid.uuid4()).split('-')[-1]
            permalink = slug_title + '-' + last_uid
            new_post.slug_title = permalink
            new_post.blog = blog
            new_post.user = request.user

            with transaction.atomic():
                new_post.save()
                form.save_m2m()

            success_path = '/'.join(request.path.split('/')[:-1])

            return redirect(success_path)
        else:
            form = MemberBlogSettingPostNewCreateForm(blog)
        
        return render(request, self.template_name, {'form': form})

    def _get_blog(self, request, **kwargs):
        username = self.kwargs['username']

        if self.request.user.username != username:
            raise Http404

        self.blog = get_object_or_404(Blog, user=request.user)

        return self.blog


