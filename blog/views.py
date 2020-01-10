from django.views.generic import TemplateView
from django.shortcuts import redirect, render
from django.contrib.auth.models import Group
from django.db import transaction
from .models import Blog, Theme
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