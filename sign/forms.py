from django import forms

class BaseRegisterForm(forms.Form):
    email = forms.EmailField(label='Email')
    name = forms.CharField(label='Имя')
    last_name = forms.CharField(label='Фамилия')
    class Meta:
        fields = [
            'username',
            'email',
            'name',
            'last_name',
            'password1',
            'password2',
        ]