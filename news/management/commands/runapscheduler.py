import logging

from apscheduler.triggers.interval import IntervalTrigger
from django.conf import settings
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django.core.mail import send_mail
from django.template.loader import render_to_string
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import User
from news.models import Post, Category, UserSubscribes  # Импортируем ваши модели

logger = logging.getLogger(__name__)



def send_weekly_articles():
    """Рассылка новых статей подписчикам"""
    one_week_ago = timezone.now() - timedelta(weeks=1)

    all_new_articles = Post.objects.filter(date_created__gte=one_week_ago).prefetch_related('category')

    for category in Category.objects.all():

        new_articles = all_new_articles.filter(category=category)

        if not new_articles:
            continue

        # Находим всех подписчиков категории
        subscribers = UserSubscribes.objects.filter(
            category=category
        ).select_related('user')

        for subscription in subscribers:
            user = subscription.user

            subject = f"Новые статьи в категории {category.name_category}"
            html_message = render_to_string('weekly_articles.html', {
                'user': user,
                'category': category,
                'articles': new_articles,
                'SITE_URL': settings.SITE_URL
            })

            send_mail(
                subject=subject,
                message="",
                html_message=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            logger.info(f"Отправлена рассылка для {user.email} по категории {category.name_category}")


def delete_old_job_executions(max_age=604_800):
    """Удаление старых записей выполненных задач"""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs APScheduler for weekly article notifications"

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # Еженедельная рассылка по понедельникам в 9:00
        scheduler.add_job(
            send_weekly_articles,
            trigger=CronTrigger(
                day_of_week="mon",
                hour=9,
                minute=0
            ),
            # trigger=IntervalTrigger(
            #     seconds=5
            # ), Для тестов, удалить в дальнейшем
            id="weekly_articles",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added weekly article notifications job")

        # Очистка старых задач каждое воскресенье в 00:00
        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="sun",
                hour=0,
                minute=0
            ),
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added weekly cleanup job")

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")