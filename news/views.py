from django.http import Http404
from django.template.context_processors import request
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from news.forms import PostFrom
from news.models import Post


# Create your views here.

class NewsList(ListView):
    model = Post
    template_name = 'news_list.html'
    ordering = '-date_created'
    context_object_name = 'news'
    paginate_by = 2

class NewsDetail(DetailView):
    model = Post
    template_name = 'news.html'
    context_object_name = 'post'

class NewsCreate(CreateView):
    form_class = PostFrom
    model = Post
    template_name = 'news_edit.html'

    def form_valid(self, form):
        news = form.save(commit=False)
        if 'news' in self.request:
            news.type_post = Post.NEWS
        elif 'article' in self.request:
            news.type_post = Post.ARTICLE
        else:
            raise(Http404())
        return super().form_valid(form)

class NewsUpdate(UpdateView):
    form_class = PostFrom
    model = Post
    template_name = 'news_edit.html'

    def form_valid(self, form):
        news = form.save(commit=False)
        if 'news' in self.request:
            news.type_post = Post.NEWS
        elif 'article' in self.request:
            news.type_post = Post.ARTICLE
        return super().form_valid(form)

class NewsDelete(DeleteView):
    model = Post
    template_name = 'news_delete.html'
    success_url = reverse_lazy('news_list')

    def get_queryset(self):
        """Дописать нормальную проверку наличия, посмотреть все методы request"""
        if 'news' in str(self.request.path).split('/'):
            return Post.objects.filter(type_post=Post.NEWS)
        #
        elif 'article' in self.request:
            return Post.objects.filter(type_post=Post.ARTICLE)
        else:
            raise(Http404())