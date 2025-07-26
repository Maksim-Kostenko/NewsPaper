from django.core.mail import send_mail

from news.models import PostCategory, UserSubscribes
from django.contrib.auth.models import User

from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=PostCategory)
def new_post_sub_notification(instance, created, **kwargs):
    if created:
        post = instance.post
        category = instance.category
        subscribers = UserSubscribes.objects.filter(category=category).select_related('user')

        subject =f'Новый пост в категории "{category.name_category}"'
        message = f'Заголовок: {post.title}\n\n{post.preview()}\n\nЧитать полностью: {post.get_absolute_url()}'
        for subscribe in subscribers:
            send_mail(
                subject=subject,
                message=message,
                from_email='totsamisamiy@yandex.ru',
                recipient_list=[subscribe.user.email],
                fail_silently=False,
            )
#todo 4: Подумать над реализацией данного метода с помощью allauth методов! Посмотреть
# исходный код DefaultAccountAdapter (отнаследоваться и просто не много добавить логики или полностью переопределить работу данного метода или
# просто создать HTML, который будет отправлятсья клиенту)
#
# @receiver(post_save, sender=User)
# def hello_user_notification(instance,created,  **kwargs):
#     """Для отправки писем, можно использовать в том случае, если отказаться от
#     использования allauth в своем проекте, поэтому на данном этапе закоментил
#     Смотреть реализациб в adapter.py"""
#     if created:
#         username = instance.username
#         email = instance.email
#         subject = f'{username}, добро пожаловать на сайт!'
#         message = f'Приятного чтения новостей!'
#         send_mail(
#             subject=subject,
#             message=message,
#             from_email='totsamisamiy@yandex.ru',
#             recipient_list=email,
#             fail_silently=False
#         )

