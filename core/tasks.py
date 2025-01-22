from  celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

# Task to send emails
@shared_task
def send_email(subject, message, recipient, content_type="text/plain"):
    """
    Task to send HTML emails using Django's EmailMultiAlternatives.
    Args:
        subject (str): Email subject.
        message (str): HTML content of the email.
        recipient (str): Recipient email address.
    """
    try:
        # Create an EmailMultiAlternatives object
        email = EmailMultiAlternatives(
            subject=subject,
            body='',  # Plain-text body
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient],
        )
        email.attach_alternative(message, content_type)
        # Send the email
        email.send()
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        raise Exception(f"Error while sending email: {str(e)}")