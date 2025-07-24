from django.core.mail import send_mail, mail_managers

from news.models import PostCategory, UserSubscribes

from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=PostCategory)
def new_post_sub_notification(sender, instance, created, **kwargs):
    post = instance.post
    category = instance.category
    subscribers = UserSubscribes.objects.filter(category=category).select_related('user')

    subject =f'Новый пост в категории "{category.name_category}"'
    for subscribe in subscribers:
        send_mail(
            subject=subject,
            message=f'Заголовок: {post.title}\n\n{post.preview()}\n\nЧитать полностью: {post.get_absolute_url()}',
            from_email='totsamisamiy@yandex.ru',
            recipient_list=[subscribe.user.email],
            fail_silently=False,
        )