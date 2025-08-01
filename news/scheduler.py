from apscheduler.schedulers.background import BackgroundScheduler

from .tasks import send_mails

news_scheduler = BackgroundScheduler()
news_scheduler.add_job(func=send_mails)