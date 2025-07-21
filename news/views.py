from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin


from news.forms import PostFrom, SubscribeForm
from news.models import Post, UserSubscribes, Category
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
        """Вывод только отфильтрованных товаров"""
        queryset = super().get_queryset()
        self.filterset = NewsFilter(self.request.GET, queryset)
        # Возвращаем из функции отфильтрованный список товаров
        return self.filterset.qs

    def get_context_data(self, *, object_list=None, **kwargs):
        """Вывод настроенных фильтров"""
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

class PostCreated(LoginRequiredMixin, CreateView, TypePostMixin):
    form_class = PostFrom
    model = Post
    template_name = 'post_edit.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.type_post = self.get_post_type()
        return super().form_valid(form)

class PostUpdate(LoginRequiredMixin, UpdateView, TypePostMixin):
    form_class = PostFrom
    model = Post
    template_name = 'post_edit.html'
    login_url = 'news_list'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.type_post = self.get_post_type()
        return super().form_valid(form)

    def get_queryset(self):
        return Post.objects.filter(type_post=self.get_post_type())

class PostDelete(LoginRequiredMixin, DeleteView, TypePostMixin):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('news_list')

    def get_queryset(self):
        return Post.objects.filter(type_post=self.get_post_type())

class CategorySubscribe(LoginRequiredMixin, FormView):
    form_class = SubscribeForm
    model = Category
    template_name = 'category_subscribe.html'
    context_object_name = 'category'
    success_url = reverse_lazy('news_list')

    def get_form_kwargs(self):
        """Передаем пользователя в форму"""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        # Удаляем старые подписки пользователя
        UserSubscribes.objects.filter(user=self.request.user).delete()

        # Добавляем новые подписки
        for category in form.cleaned_data['categories']:
            UserSubscribes.objects.create(
                user=self.request.user,
                category=category
            )
        return super().form_valid(form)
