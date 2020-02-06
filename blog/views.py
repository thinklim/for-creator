import uuid
from django.views.generic import CreateView, DetailView, ListView, TemplateView, UpdateView
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import Group, User
from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction
from django.db.models import Q
from django.http import Http404, JsonResponse
from django.utils.text import slugify
from rest_framework import generics
from .models import Attachment, Blog, Category, Theme, Post, Tag
from .forms import BlogCreateForm, MemberBlogSettingPostCreateAndEditForm, UploadImageFileForm


class BlogView(ListView):
    model = Post
    paginate_by = 6
    template_name = 'blog/blog.html'

    def get_queryset(self):
        search_type = self.request.GET.get('search-type', '')
        value = self.request.GET.get('value', '')

        if search_type and value:
            if search_type == 'question':
                return Post.objects.filter(Q(title__icontains=value) | Q(content__icontains=value) | Q(blog__name__icontains=value) | Q(user__username__icontains=value)).order_by('-id')

        return Post.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['themes'] = Theme.objects.all()
        search_type = self.request.GET.get('search-type', '')
        value = self.request.GET.get('value', '')

        if search_type and value:
            context['search_type'] = search_type
            context['value'] = value

        return context

class BlogCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    form_class = BlogCreateForm
    login_url = '/login'
    permission_required = 'blog.add_blog'
    redirect_field_name = '/login'
    success_url = '/blog'
    template_name = 'blog/blog.html'

    def get(self, request, *args, **kwargs):
        return redirect('/blog')

    def form_valid(self, form):
        with transaction.atomic():
            request_user = self.request.user
            new_blog = form.save(commit=False)
            new_blog.user = request_user
            new_blog.save()

            blogger_group = Group.objects.get(name='Blogger')
            blogger_group.user_set.add(request_user)
            
            member_group = Group.objects.get(name='Member')
            request_user.groups.remove(member_group)
        return super().form_valid(form)

class MemberBlogView(ListView):
    model = Post
    paginate_by = 4
    template_name = 'blog/member_blog.html'

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs['username'])
        search_type = self.request.GET.get('search-type', '')
        value = self.request.GET.get('value', '')

        if search_type and value:
            if search_type == 'question':
                return Post.objects.filter(Q(title__icontains=value) | Q(content__icontains=value), user=user).order_by('-id')
            elif search_type == 'category':
                return Post.objects.filter(user=user, category__slug_name=value).order_by('-id')
            elif search_type == 'tag':
                return Post.objects.filter(user=user, tag__slug_name=value).order_by('-id')

        return Post.objects.filter(user=user).order_by('-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(User, username=self.kwargs['username'])
        blog =  Blog.objects.get(user=user)
        context['blog'] = blog
        context['categories'] = Category.objects.filter(blog=blog)
        context['tags'] = Tag.objects.filter(blog=blog)

        search_type = self.request.GET.get('search-type', '')
        value = self.request.GET.get('value', '')

        if search_type and value:
            context['search_type'] = search_type
            context['value'] = value

        return context

class MemberBlogPostDetailView(DetailView):
    model = Post
    slug_field = 'slug_title'
    slug_url_kwarg = 'slug_title'
    template_name = 'blog/member_blog_post_detail.html'

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs['username'])
        
        return Post.objects.filter(user=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['blog'] = context['post'].blog

        return context

class MemberBlogSettingView(TemplateView):
    template_name = 'blog/member_blog_setting.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        blog = get_owner_blog(self)
        context['blog'] = blog
        
        return context

class MemberBlogSettingPostListView(ListView):
    model = Post
    paginate_by = 4
    template_name = 'blog/member_blog_setting_post.html'

    def get_queryset(self):
        blog = get_owner_blog(self)
        search_type = self.request.GET.get('search-type', '')
        value = self.request.GET.get('value', '')

        if search_type and value:
            if search_type == 'question':
                return Post.objects.filter(Q(title__icontains=value) | Q(content__icontains=value), blog=blog).order_by('-id')

        return Post.objects.filter(blog=blog).order_by('-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_type = self.request.GET.get('search-type', '')
        value = self.request.GET.get('value', '')

        if search_type and value:
            context['search_type'] = search_type
            context['value'] = value
    
        return context

class MemberBlogSettingPostCreateView(CreateView):
    template_name = 'blog/member_blog_setting_post_new.html'

    def get(self, request, *args, **kwargs):
        context = {'form': MemberBlogSettingPostCreateAndEditForm(get_owner_blog(self))}

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        blog = get_owner_blog(self)
        form = MemberBlogSettingPostCreateAndEditForm(blog, request.POST, request.FILES)

        if form.is_valid():
            with transaction.atomic():
                new_tags = get_new_tags(self, form.cleaned_data['tag'])
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
            form = MemberBlogSettingPostCreateAndEditForm(blog)
        
        return render(request, self.template_name, {'form': form})

class MemberBlogSettingPostEditView(UpdateView):
    template_name = 'blog/member_blog_setting_post_edit.html'

    def get(self, request, *args, **kwargs):
        post = Post.objects.get(id=self.kwargs['pk'])
        tags = [tag.name for tag in list(post.tag.all())]
        tag_text = ','.join(tags)

        initial_data = {'title': post.title, 'thumbnail':  post.thumbnail, 'category': post.category, 'tag':  tag_text, 'content': post.content}
        context = {'form': MemberBlogSettingPostCreateAndEditForm(get_owner_blog(self), initial=initial_data)}

        print(context)

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        blog = get_owner_blog(self)
        form = MemberBlogSettingPostCreateAndEditForm(blog, request.POST, request.FILES)

        if form.is_valid():
            with transaction.atomic():
                post = Post.objects.get(id=self.kwargs['pk'])
                form_tag = get_new_tags(self, form.cleaned_data['tag'])
                form_title = form.cleaned_data['title']

                post.thumbnail = form.cleaned_data['thumbnail']
                post.category = form.cleaned_data['category']
                post.content = form.cleaned_data['content']

                if post.title is not form_title:
                    post.title = form_title
                    post.slug_title = get_permalink(post.title)
                
                post.tag.set(form_tag)
                post.save()

            success_path = '/'.join(request.path.split('/')[:-1])

            return redirect(success_path)
        else:
            form = MemberBlogSettingPostCreateAndEditForm(blog)
        
        return render(request, self.template_name, {'form': form})

class MemberBlogSettingCategoryListView(ListView):
    template_name = 'blog/member_blog_setting_category.html'

    def get_queryset(self, *kwargs):
        blog= get_owner_blog(self)

        return Category.objects.filter(blog=blog).order_by('-id')

class MemberBlogSettingTagListView(ListView):
    template_name = 'blog/member_blog_setting_tag.html'

    def get_queryset(self, **kwargs):
        blog = get_owner_blog(self)

        return Tag.objects.filter(blog=blog).order_by('-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tags = [tag.name + '${}'.format(tag.id) for tag in list(context['object_list'])]
        tag_text = ','.join(tags)
        context['tag_text'] = tag_text

        return context

@login_required
@permission_required('blog.add_attachment')
def upload(request):
    if request.method == 'POST':
        form = UploadImageFileForm(request.POST, request.FILES)

        if form.is_valid():
            blog = Blog.objects.get(user=request.user)
            image = request.FILES['image']

            attachment = Attachment(blog=blog, name=image.name, image=image)
            attachment.save()

            return JsonResponse({'message': 'success', 'location': attachment.image.url})
        else:
            return JsonResponse({'message': 'form is invalid'})

def get_owner_blog(self):
    request_user = self.request.user
    url_path_username = self.kwargs['username']
    
    if request_user.username != url_path_username:
        raise Http404
    
    return get_object_or_404(Blog, user=request_user)

def get_new_tags(self, tag_text):
    blog = get_owner_blog(self)
    new_tags = []
    
    if tag_text:
        for tag_data in tag_text.split(','):
            new_tag, is_created = Tag.objects.get_or_create(blog=blog, name=tag_data, defaults={'slug_name': get_permalink(tag_data)})
            new_tags.append(new_tag)
    
    return new_tags

def get_permalink(text):
    slug = slugify(text, allow_unicode=True)
    last_uid = str(uuid.uuid4()).split('-')[-1]
    permalink = slug + '-' + last_uid

    return permalink
