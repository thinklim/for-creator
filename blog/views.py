import uuid
from django.views.generic import CreateView, DetailView, ListView, TemplateView, UpdateView
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.models import Group, User
from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction
from django.http import Http404, JsonResponse
from django.utils.text import slugify
from .models import Attachment, Blog, Category, Theme, Post, Tag
from .forms import BlogCreateForm, MemberBlogSettingPostNewCreateForm, MemberBlogSettingPostEditForm, UploadImageFileForm

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
            with transaction.atomic():
                new_tags = self._get_new_tags(request, form.cleaned_data['tag'])
                form.cleaned_data['tag'] = new_tags

                new_post = form.save(commit=False)
                new_post.slug_title = get_permalink(new_post.title)
                new_post.blog = blog
                new_post.user = request.user
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

    def _get_new_tags(self, request, tag_data):
        blog = self._get_blog(request)
        new_tags = []

        if tag_data:
            for tag_data in tag_data.split(','):
                new_tag, is_created = Tag.objects.get_or_create(blog=blog, name=tag_data, defaults={'slug_name': get_permalink(tag_data)})
                new_tags.append(new_tag)
        
        return new_tags

def get_permalink(text):
    slug = slugify(text, allow_unicode=True)
    last_uid = str(uuid.uuid4()).split('-')[-1]
    permalink = slug + '-' + last_uid

    return permalink

@login_required
@permission_required('blog.add_attachment')
def upload(request):
    if request.method == 'POST':
        blog = Blog.objects.get(user=request.user)
        form = UploadImageFileForm(blog, request.POST, request.FILES)

        if form.is_valid():
            image = request.FILES['image']

            instance = Attachment(name=image.name, image=image, blog=blog)
            instance.save()

            return JsonResponse({'message': 'success', 'location': instance.image.url})
        else:
            return JsonResponse({'message': 'form is invalid'})

class MemberBlogSettingPostEditView(UpdateView):
    template_name = 'blog/member_blog_setting_post_edit.html'

    def get(self, request, *args, **kwargs):
        post = Post.objects.get(id=self.kwargs['pk'])
        tags = [tag.name for tag in list(post.tag.all())]
        tag_text = ','.join(tags)

        initial_data = {'title': post.title, 'thumbnail':  post.thumbnail, 'category': post.category, 'tag':  tag_text, 'content': post.content}
        context = {'form': MemberBlogSettingPostNewCreateForm(self._get_blog(request), initial=initial_data)}

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        blog = self._get_blog(request)
        form = MemberBlogSettingPostEditForm(blog, request.POST, request.FILES)

        if form.is_valid():
            with transaction.atomic():
                post = Post.objects.get(id=self.kwargs['pk'])
                form_tag = self._get_new_tags(request, form.cleaned_data['tag'])
                form_title = form.cleaned_data['title']

                post.thumbnail = form.cleaned_data['thumbnail']
                post.category = form.cleaned_data['category']
                post.content = form.cleaned_data['content']

                if post.title != form_title:
                    post.title = form_title
                    post.slug_title = get_permalink(post.title)
                
                post.tag.set(form_tag)
                post.save()

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

    def _get_new_tags(self, request, tag_data):
        blog = self._get_blog(request)
        new_tags = []

        if tag_data:
            for tag_data in tag_data.split(','):
                new_tag, is_created = Tag.objects.get_or_create(blog=blog, name=tag_data, defaults={'slug_name': get_permalink(tag_data)})
                new_tags.append(new_tag)
        
        return new_tags