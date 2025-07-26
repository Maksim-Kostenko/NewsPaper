from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string


class CustomAccountAdapter(DefaultAccountAdapter):
    def send_confirmation_mail(self, request, emailconfirmation, signup):
        user = emailconfirmation.email_address.user
        ctx = {
            "user": user,
            "key": emailconfirmation.key,
            "request": request,
            "site_name": settings.SITE_NAME
        }

        # Рендерим шаблоны
        subject = render_to_string(
            'account/email/email_confirmation_subject.txt',
            ctx
        )
        message_html = render_to_string(
            'account/email/email_confirmation_message.html',
            ctx
        )
        message_plain = render_to_string(
            'account/email/email_confirmation_message.txt',
            ctx
        )

        send_mail(
            subject=subject.strip(),
            message=message_plain,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[emailconfirmation.email_address.email],
            html_message=message_html
        )