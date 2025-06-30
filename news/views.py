from django.views.generic import ListView, DetailView

from news.models import Post


# Create your views here.

class NewsList(ListView):
    model = Post
    template_name = 'news_list.html'
    ordering = '-date_created'
    context_object_name = 'news'

class NewsDetail(DetailView):
    model = Post
    template_name = 'news.html'
    context_object_name = 'post'
