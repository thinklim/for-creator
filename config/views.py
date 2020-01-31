from django.contrib.auth.models import Group, User
from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.shortcuts import render, redirect
from django.views.generic import CreateView, TemplateView
from .forms import JoinForm


class IndexView(TemplateView):
    template_name = 'index.html'

class JoinView(CreateView):
    form_class = JoinForm
    success_url = '/login'
    template_name = 'join.html'

    def form_valid(self, form):
        with transaction.atomic():
            new_user = form.save(commit=False)
            new_user.password = make_password(new_user.password)
            new_user.save()

            member_group = Group.objects.get(name='Member')
            member_group.user_set.add(new_user)
        
        return super().form_valid(form)


    
