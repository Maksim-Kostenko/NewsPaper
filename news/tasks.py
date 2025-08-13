from collections import defaultdict
from datetime import timedelta
from django.utils import timezone
from smtplib import SMTPException
from sqlite3 import DatabaseError

from celery import shared_task
from django.core.mail import send_mass_mail, send_mail
from django.conf import settings
import logging

from django.db.models import Prefetch
from django.template.loader import render_to_string

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

        subject = (f'Новый пост в категории "{first_category_name}"'
                   if categories.count() == 1
                   else f'Новый пост в категориях: {all_categories}')


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

@shared_task()
def send_weekly_digest(self):
    """Рассылка еженедельного дайджеста новых статей"""
    try:
        one_week_ago = timezone.now() - timedelta(weeks=1)

        # 1. Получаем все новые статьи за неделю с категориями
        new_articles = (
            Post.objects
            .filter(date_created__gte=one_week_ago, type_post=Post.ARTICLE)
            .prefetch_related('category')
            .order_by('-date_created')
        )

        if not new_articles.exists():
            logger.info("No new articles for weekly digest")
            return

        # 2. Получаем всех подписчиков с их категориями
        subscribers = (
            UserSubscribes.objects
            .filter(category__post__in=new_articles)
            .select_related('user', 'category')
            .distinct()
        )

        if not subscribers.exists():
            logger.info("No subscribers for weekly digest")
            return

        # 3. Группируем статьи по категориям
        articles_by_category = defaultdict(list)
        for article in new_articles:
            for category in article.category.all():
                articles_by_category[category].append(article)

        # 4. Группируем подписчиков по пользователю
        user_subscriptions = defaultdict(list)
        for sub in subscribers:
            if sub.user.email:  # Только пользователи с email
                user_subscriptions[sub.user].append(sub.category)

        # 5. Отправляем персонализированные дайджесты
        for user, categories in user_subscriptions.items():
            try:
                # Собираем все статьи пользователя по его подпискам
                user_articles = []
                for category in categories:
                    user_articles.extend(articles_by_category.get(category, []))

                if not user_articles:
                    continue

                # Убираем дубликаты статей (если в нескольких категориях)
                unique_articles = list({article.id: article for article in user_articles}.values())

                subject = f"Еженедельный дайджест новых статей"
                html_message = render_to_string('weekly_articles.html', {
                    'user': user,
                    'articles': unique_articles,
                    'categories': categories,
                })

                send_mail(
                    subject=subject,
                    message="",  # Текстовая версия будет в html_message
                    html_message=html_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
                logger.info(f"Sent weekly digest to {user.email}")

            except Exception as e:
                logger.error(f"Failed to send digest to {user.email}: {str(e)}")
                continue

        logger.info(f"Weekly digest sent to {len(user_subscriptions)} users")

    except Exception as e:
        logger.error(f"Error in weekly digest task: {str(e)}")
        self.retry(exc=e, countdown=60 * 10)  # Повторить через 10 минут
