from news.models import PostCategory, UserSubscribes, Post
from news.tasks import new_post_sub_notification, hello

from django.core.mail import send_mail
from django.contrib.auth.models import Group

from allauth.account.signals import email_confirmed

from django.db.models.signals import post_save
from django.dispatch import receiver

import logging
logger = logging.getLogger(__name__)

@receiver(post_save, sender=Post)
def news_created(instance, created, **kwargs):
    if created:
        hello.delay()
        new_post_sub_notification.delay(instance.id)


    # if created:
    #     post = instance.post
    #     category = instance.category
    #     subscribers = UserSubscribes.objects.filter(category=category).select_related('user')
    #
    #     subject =f'Новый пост в категории "{category.name_category}"'
    #     message = f'Заголовок: {post.title}\n\n{post.preview()}\n\nЧитать полностью: {post.get_absolute_url()}'
    #     for subscribe in subscribers:
    #         send_mail(
    #             subject=subject,
    #             message=message,
    #             from_email='totsamisamiy@yandex.ru',
    #             recipient_list=[subscribe.user.email],
    #             fail_silently=False,
    #         )


@receiver(email_confirmed)
def handle_email_confirmation(request, email_address, **kwargs):
    """Действия выполняемые после подтверждения почты пользователя"""
    user = email_address.user

    _add_user_to_common_group(user)

    _send_welcome_email(user)


def _add_user_to_common_group(user):
    """Ответственность: только работа с группами"""


    try:
        common_group, created = Group.objects.get_or_create(name='common')
        if not user.groups.filter(name='common').exists():
            #Делается доп проверка
            common_group.user_set.add(user)
            # logger.info(f"Added user {user.username} to 'common' group")
            print(f"Added user {user.username} to 'common' group")
    except Exception as e:
        # logger.error(f"Error adding user to group: {str(e)}")
        print(f"Error adding user to group: {str(e)}")


def _send_welcome_email(user):
    """Ответственность: только отправка email"""
    try:
        send_mail(
            subject=f'{user.username}, добро пожаловать на сайт!',
            message='Ваш email подтвержден! Приятного чтения новостей!',
            from_email='totsamisamiy@yandex.ru', #сделать ссылку на settings
            recipient_list=[user.email],
            fail_silently=False
        )
        # logger.info(f"Welcome email sent to {user.email}")
        print(f"Welcome email sent to {user.email}")
    except Exception as e:
        # logger.error(f"Error sending welcome email: {str(e)}")
        print(f"Error sending welcome email: {str(e)}")
