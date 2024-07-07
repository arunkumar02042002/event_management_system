
from celery import shared_task

from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import send_mail
import logging

User = get_user_model()

# Get an instance of a logger
logger = logging.getLogger('__file__')

@shared_task()
def send_email(subject, message, to_email):
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[to_email],
            fail_silently=False
        )
        logger.info(f"Email sent successfully to {to_email} with subject: {subject}")
    except Exception as e:
        logger.error(f"Failed to send email to {to_email} with subject: {subject}. Error: {str(e)}")

