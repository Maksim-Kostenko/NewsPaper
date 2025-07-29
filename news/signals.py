from django.core.mail import send_mail
from django.contrib.auth.models import Group


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
def handle_email_confirmation(request, email_address, **kwargs):
    """Действия выполняемые после подтверждения почты пользователя"""
    user = email_address.user

    _add_user_to_common_group(user)

    _send_welcome_email(user)


def _add_user_to_common_group(user):
    """Ответственность: только работа с группами"""

    #todo 3: Подумат ьнеобходимо ли реализовывать common_group, created = Group.objects.get_or_create(name='common')
    # (Если создана, то created == False), а также соответственно if created нужно логировать, для того чтобы в
    # дальнейшем разобраться почему не найдена данная группа, плюс оповещение администраторов

    try:
        common_group = Group.objects.get(name='common')
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
            from_email='totsamisamiy@yandex.ru',
            recipient_list=[user.email],
            fail_silently=False
        )
        # logger.info(f"Welcome email sent to {user.email}")
        print(f"Welcome email sent to {user.email}")
    except Exception as e:
        # logger.error(f"Error sending welcome email: {str(e)}")
        print(f"Error sending welcome email: {str(e)}")
