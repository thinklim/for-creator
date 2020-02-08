from django.contrib import messages
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

            messages.success(self.request, '''<strong>회원가입에 성공했습니다!</strong>
            이제 당신의 계정으로 로그인 할 수 있습니다.''')
        
        return super().form_valid(form)


    
