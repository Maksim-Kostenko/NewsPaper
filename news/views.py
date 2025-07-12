from django.template.context_processors import request
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from news.forms import PostFrom
from news.models import Post
from news.filters import NewsFilter


# Create your views here.

class NewsList(ListView):
    model = Post
    template_name = 'news_list.html'
    ordering = '-date_created'
    context_object_name = 'news'
    paginate_by = 10

class NewsListSearch(ListView):
    model = Post
    template_name = 'news_list_search.html'
    ordering = '-date_created'
    context_object_name = 'news'
    paginate_by = 5

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = NewsFilter(self.request.GET, queryset)
        # Возвращаем из функции отфильтрованный список товаров
        return self.filterset.qs

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context

class NewsDetail(DetailView):
    model = Post
    template_name = 'news.html'
    context_object_name = 'post'

class TypePostMixin:
    """Определение типа поста"""

    def get_post_type(self) -> object:
        if 'article' in self.request.path:
            return Post.ARTICLE
        else:
            return Post.NEWS

class PostCreated(CreateView, TypePostMixin):
    form_class = PostFrom
    model = Post
    template_name = 'post_edit.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.type_post = self.get_post_type()
        return super().form_valid(form)

class PostUpdate(UpdateView, TypePostMixin):
    form_class = PostFrom
    model = Post
    template_name = 'post_edit.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.type_post = self.get_post_type()
        return super().form_valid(form)

    def get_queryset(self):
        return Post.objects.filter(type_post=self.get_post_type())

class PostDelete(DeleteView, TypePostMixin):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('news_list')

    def get_queryset(self):
        return Post.objects.filter(type_post=self.get_post_type())

