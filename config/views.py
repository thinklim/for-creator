from django.views.generic import View, TemplateView
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .forms import JoinForm


class IndexView(TemplateView):
    template_name = 'index.html'

class JoinView(View):
    template_name = 'join.html'
    form_class = JoinForm

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            user_input_data = form.cleaned_data
            user = User.objects.create_user(user_input_data['username'], user_input_data['email'], user_input_data['password'])
            user.save()

            return redirect('/login')

        return render(request, self.template_name)


    
