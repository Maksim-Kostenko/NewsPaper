from django import forms

from news.models import Post

class PostFrom(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'type_post', 'author', 'category']