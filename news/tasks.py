import time
from smtplib import SMTPException
from sqlite3 import DatabaseError

from celery import shared_task
from django.core.mail import send_mass_mail
from django.conf import settings
import logging

from django.db.models import Prefetch

from news.models import *

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def new_post_sub_notification(self, pk):
    """Отправка уведомлений подписчикам о новом посте"""
    try:
        # 1. Получаем пост с категориями
        post = Post.objects.prefetch_related(
            Prefetch('category', queryset=Category.objects.only('name_category'))
        ).only('title', 'content').get(pk=pk)

        # 2. Получаем email подписчиков
        subscriber_emails = list(
            UserSubscribes.objects
            .filter(category__in=post.category.all())
            .select_related('user')
            .values_list('user__email', flat=True)
            .distinct()
        )

        if not subscriber_emails:
            logger.info(f"No subscribers for post {pk}")
            return

        # 3. Формируем письмо
        categories = post.category.all()

        if not categories.exists():
            logger.info(f"Post {pk} has no categories")
            return

        first_category_name = categories.first().name_category
        all_categories = ", ".join([cat.name_category for cat in categories])

        subject = f'Новый пост в категории "{first_category_name}"' if categories.count() > 1 \
            else subject = f'Новый пост в категориях: {all_categories}'


        post_url = f"{settings.SITE_URL}{post.get_absolute_url()}"
        message = f'''Заголовок: {post.title}

                        {post.preview()}
                        
                        Читать полностью: {post_url}'''

        # 4. Отправляем письма
        try:
            send_mass_mail([(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email]
            ) for email in subscriber_emails if email], fail_silently=False)

            logger.info(f"Successfully sent to {len(subscriber_emails)} subscribers")
        except SMTPException as e:
            logger.error(f"Email sending failed for post {pk}: {str(e)}")
            raise
        except ConnectionRefusedError as e:
            logger.error(f"Mail server connection refused: {str(e)}")
            raise self.retry(exc=e, countdown=300)

    except Post.DoesNotExist as e:
        logger.error(f"Post {pk} not found: {str(e)}")
        raise self.retry(exc=e, countdown=60)
    except DatabaseError as e:
        logger.error(f"Database error: {str(e)}")
        raise self.retry(exc=e, countdown=120)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise self.retry(exc=e, countdown=300)