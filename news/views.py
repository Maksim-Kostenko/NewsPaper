from django.views.generic import ListView, DetailView

from news.models import Post


# Create your views here.
#todo: 1. Скорректировать view и html, чтобы было более читабельно, а также скорректировать html
#todo: 2. Выводите новости в следующем виде — заголовок, дата публикации в формате день.месяц.год, затем первые 20 слов текста статьи. Можно вывести как списком, так и таблицей. Новости должны выводиться в порядке от более свежей к старой.
#todo: 3. Сверху страницы должно быть выведено количество всех новостей (используется фильтр news|length).
#todo: 4. По ссылке /news/<id новости> должна выводиться детальная информация о новости.
#todo: 5. Заголовок, дата публикации в формате день.месяц.год и полный текст статьи.


class NewsList(ListView):
    model = Post
    template_name = 'news_list.html'
    ordering = 'date_created'
    context_object_name = 'news'

class NewsDetail(DetailView):
    model = Post
    template_name = 'news.html'
    context_object_name = 'post'

