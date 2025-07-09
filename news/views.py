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
    paginate_by = 2

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

class NewsCreate(CreateView):
    form_class = PostFrom
    model = Post
    template_name = 'post_edit.html'

    def form_valid(self, form):
        news = form.save(commit=False)
        news.type_post = Post.NEWS
        return super().form_valid(form)

class NewsUpdate(UpdateView):
    form_class = PostFrom
    model = Post
    template_name = 'post_edit.html'

    def form_valid(self, form):
        """Реализовано принудительное изменение типа поста,
        независимо от того что выберет редактор"""
        news = form.save(commit=False)
        news.type_post = Post.NEWS
        return super().form_valid(form)

    def get_queryset(self):
        return Post.objects.filter(type_post=Post.NEWS)

class NewsDelete(DeleteView):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('news_list')

    def get_queryset(self):
        return Post.objects.filter(type_post=Post.NEWS)


class ArticleCreate(CreateView):
    form_class = PostFrom
    model = Post
    template_name = 'post_edit.html'

    def form_valid(self, form):
        news = form.save(commit=False)
        news.type_post = Post.ARTICLE
        return super().form_valid(form)


class ArticleUpdate(UpdateView):
    form_class = PostFrom
    model = Post
    template_name = 'post_edit.html'

    def form_valid(self, form):
        news = form.save(commit=False)
        news.type_post = Post.ARTICLE
        return super().form_valid(form)

    def get_queryset(self):
        return Post.objects.filter(type_post=Post.ARTICLE)


class ArticleDelete(DeleteView):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('news_list')

    def get_queryset(self):
        return Post.objects.filter(type_post=Post.ARTICLE)

# Делать общий класс не очень правильно, на сколько я понимаю в соответствии с принципами SOLID, но тоже спорный момент,
# но  в целом можно реализовать и для функций create и Update
# такую же логику проверки в request наличия news или article, а после чего уже и фильтровать либо по NEWS или по ARTICLE
#что то на подобии
        # def form_valid(self, form):
        #   post = form.save(commit=False)
        #   if 'news' in str(self.request.path).split('/'):
        #       post.type_post = Post.NEWS
        #   elif 'article' in str(self.request.path).split('/'):
        #       post.type_post = Post.ARTICLE
        #   return super().form_valid(form)
# class NewsDelete(DeleteView):
#     model = Post
#     template_name = 'post_delete.html'
#     success_url = reverse_lazy('news_list')
#
#     def get_queryset(self):
#         """Дописать нормальную проверку наличия, посмотреть все методы request"""
#         if 'news' in str(self.request.path).split('/'):
#             return Post.objects.filter(type_post=Post.NEWS)
#         elif 'article' in str(self.request.path).split('/'):
#             return Post.objects.filter(type_post=Post.ARTICLE)
#         else:
#             raise(Http404())

