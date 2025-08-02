from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.shortcuts import redirect
from django.views.generic import TemplateView

from news.models import Author


# Create your views here.
class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'protect/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['is_not_author'] = not self.request.user.groups.filter(name='author').exists()
        return context

@login_required
def upgrade_author(request):
    user = request.user
    premium_group, created  = Group.objects.get_or_create(name='author')
    if not request.user.groups.filter(name='author').exists():
        premium_group.user_set.add(user)
        if not Author.objects.filter(user=user).exists():
            Author.objects.create(user=user)
        else:
            print('Что то пошло не так при добавлении пользователя в БД Авторов')
            #Сделать логирование
    return redirect('/')
