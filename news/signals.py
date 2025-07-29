from django.core.mail import send_mail

from news.models import PostCategory, UserSubscribes
from allauth.account.signals import email_confirmed

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


@receiver(email_confirmed)
def hello_user_notification(request, email_address, **kwargs):
    user = email_address.user
    subject = f'{user.username}, добро пожаловать на сайт!'
    message = f'Ваш email подтвержден! Приятного чтения новостей!'
    send_mail(
        subject=subject,
        message=message,
        from_email='totsamisamiy@yandex.ru',
        recipient_list=[user.email],
        fail_silently=False
    )

