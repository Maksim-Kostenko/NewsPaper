from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mass_mail
from django.conf import settings
import logging

from news.models import *

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)  # Добавляем bind=True для self.retry
def new_post_sub_notification(self, pk):
    try:
        # 1. Получаем пост и подписчиков
        post = Post.objects.select_related('category').only(
            'title', 'text', 'category__name_category'
        ).get(pk=pk)

        subscribers = UserSubscribes.objects.filter(
            category=post.category
        ).select_related('user').only('user__email')

        if not subscribers.exists():
            logger.info(f"No subscribers for post {pk}")
            return

        # 2. Формируем письма
        subject = f'Новый пост в категории "{post.category.name_category}"'
        message = f'Заголовок: {post.title}\n\n{post.preview()}\n\nЧитать полностью: {post.get_absolute_url()}'

        messages = [
            (subject, message, settings.DEFAULT_FROM_EMAIL, [sub.user.email])
            for sub in subscribers
        ]

        # 3. Отправляем
        try:
            send_mass_mail(messages, fail_silently=False)
            logger.info(f"Successfully sent {len(messages)} emails for post {pk}")
        except Exception as e:
            logger.error(f"Email sending failed for post {pk}: {str(e)}")
            raise  # Повторяем всю задачу

    except ObjectDoesNotExist as e:
        logger.error(f"Post {pk} not found, retrying: {str(e)}")
        self.retry(exc=e, countdown=60)
    except Exception as e:
        logger.error(f"Unexpected error for post {pk}, retrying: {str(e)}")
        self.retry(exc=e, countdown=120)