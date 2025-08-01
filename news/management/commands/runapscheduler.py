from django.core.management.base import BaseCommand
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler import util
from django.conf import settings

def my_scheduled_job():
    print("Выполняется задача по расписанию!")
    # Здесь ваша логика (например, рассылка статей)

class Command(BaseCommand):
    help = "Запускает APScheduler"

    def handle(self, *args, **options):
        scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # Добавляем задачу (например, каждые 10 минут)
        scheduler.add_job(
            my_scheduled_job,
            trigger="interval",
            minutes=10,
            id="my_job",
            max_instances=1,
            replace_existing=True,
        )

        try:
            self.stdout.write(self.style.SUCCESS("Запуск планировщика..."))
            scheduler.start()
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("Остановка планировщика..."))
            scheduler.shutdown()