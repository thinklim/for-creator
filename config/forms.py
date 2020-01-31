from django import forms
from django.contrib.auth.models import User


join_form_tags = {'username': '아이디', 'email': '이메일', 'password': '비밀번호'}

class JoinForm(forms.ModelForm):
    class Meta:
        model = User
        fields = join_form_tags.keys()
        widgets = {
            'password': forms.PasswordInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for key, value in join_form_tags.items():
            field = self.fields[key]

            if key is not 'email':
                field.widget.attrs.update({'minlength': 8, 'maxlength': 30})
                field.label  = value + '(필수*)'
            else:
                field.label  = value + '(선택)'

            field.widget.attrs.update({'class': 'au-input au-input--full', 'placeholder': value})
