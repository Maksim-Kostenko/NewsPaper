from django import forms

from news.models import Post, Category


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'category']

class SubscribeForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Получаем пользователя из kwargs
        super().__init__(*args, **kwargs)

        # Настраиваем queryset для выбора категорий
        self.fields['categories'] = forms.ModelMultipleChoiceField(
            queryset=Category.objects.all(),
            widget=forms.CheckboxSelectMultiple,
            required=False
        )

        # Устанавливаем начальные значения для уже подписанных категорий
        if self.user and self.user.is_authenticated:
            self.fields['categories'].initial = Category.objects.filter(
                subscribes=self.user
            ).values_list('id', flat=True)