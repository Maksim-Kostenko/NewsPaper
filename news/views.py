from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin


from news.forms import PostForm, SubscribeForm
from news.models import Post, UserSubscribes, Category
from news.filters import NewsFilter

from datetime import date

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
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'

    def form_valid(self, form):
        posts_today = Post.objects.filter(
            author=self.request.user.author,
            date_created__date=date.today()
        )

        if posts_today.count() >= 3:

            form.add_error(None, f'{self.request.user.username}, вы уже создали 3 поста сегодня. Попробуйте завтра.')
            return self.form_invalid(form)

        post = form.save(commit=False)
        post.author = self.request.user.author
        post.type_post = self.get_post_type()
        post.content = post.content
        post.save()
        form.save_m2m()
        post_categories = post.category.all()

        # for category in post_categories:
        #     subscribers = UserSubscribes.objects.filter(
        #         category=category
        #     ).select_related('user')
        #
        #     for subscription in subscribers:
        #         self.send_notification_email(
        #             user=subscription.user,
        #             post=post,
        #             category=category
        #         )

        return super().form_valid(form)

    # def send_notification_email(self, user, post, category):
    #
    #     subject = f'Новая новость в категории "{category.name_category}"'
    #
    #     text_content = f"""
    #     Здравствуйте, {user.username}!
    #
    #     Новая новость в категории "{category.name_category}":
    #     {post.title}
    #
    #     {post.content[:50]}...
    #
    #     Читать полностью: {post.get_absolute_url()}
    #     """
    #
    #     html_content = render_to_string(
    #         'new_post_notification.html',
    #         {
    #             'user': user,
    #             'post': post,
    #             'content': post.content[:50],
    #             'category': category,
    #             'site_name': 'Ваш сайт'
    #         }
    #     )
    #
    #     msg = EmailMultiAlternatives(
    #         subject=subject,
    #         body=text_content,
    #         from_email='totsamisamiy@yandex.ru',
    #         to=[user.email],
    #     )
    #     msg.attach_alternative(html_content, "text/html")
    #     msg.send(fail_silently=False)

class PostUpdate(LoginRequiredMixin, UpdateView, TypePostMixin):
    form_class = PostForm
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
    """
    Возможность подписок на разные категории новостей
    """
    form_class = SubscribeForm
    model = Category
    template_name = 'category_subscribe.html'
    context_object_name = 'category'
    success_url = reverse_lazy('news_list')

    def get_form_kwargs(self):
        """Передаем пользователя в форму (для получения действующих подписок пользователя)"""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        """Создания подписок на категории"""
        UserSubscribes.objects.filter(user=self.request.user).delete()

        for category in form.cleaned_data['categories']:
            UserSubscribes.objects.create(
                user=self.request.user,
                category=category
            )
        return super().form_valid(form)