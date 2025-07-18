from allauth.account.forms import SignupForm
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group


class BaseRegisterForm(UserCreationForm):
    email = forms.EmailField(label='Email')
    name = forms.CharField(label='Имя')
    last_name = forms.CharField(label='Фамилия')
    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'name',
            'last_name',
            'password1',
            'password2',
        ]


class BasicSignupForm(SignupForm):

    def save(self, request):
        user = super(BasicSignupForm,self).save(request)
        basic_group = Group.objects.get(name="common")
        basic_group.user_set.add(user)
        return user
