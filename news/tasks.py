import time

from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mass_mail, send_mail
from django.conf import settings
import logging

from django.db.models import Prefetch

from news.models import *

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def new_post_sub_notification(self, pk):
    """ИСправить получение почты!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"""
    try:
        # 1. Получаем пост и подписчиков
        post = Post.objects.prefetch_related(
            Prefetch('category', queryset=Category.objects.only('name_category'))
        ).only('title', 'content').get(pk=pk)

        subscriber_emails = (UserSubscribes.objects
                             .filter(category__in=post.category.all())
                             .select_related('user')
                             .values_list('user__email', flat=True)
                             .distinct()  # Убираем дубликаты
                             )

        if not subscriber_emails:
            logger.info(f"No subscribers for post {pk}")
            return

        # 2. Формируем письма
        subject = f'Новый пост в категории "{post.category.first().name_category}"'
        message = f'Заголовок: {post.title}\n\n{post.preview()}\n\nЧитать полностью: {post.get_absolute_url()}'


        # 3. Отправляем
        try:
            send_mass_mail([(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email]
            ) for email in subscriber_emails if email], fail_silently=False)

            logger.info(f"Sent to {len(subscriber_emails)} subscribers")
        except Exception as e:
            logger.error(f"Email sending failed for post {pk}: {str(e)}")
            raise  # Повторяем всю задачу

    except ObjectDoesNotExist as e:
        logger.error(f"Post {pk} not found, retrying: {str(e)}")
        self.retry(exc=e, countdown=60)
    except Exception as e:
        logger.error(f"Unexpected error for post {pk}, retrying: {str(e)}")
        self.retry(exc=e, countdown=120)