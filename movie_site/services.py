from .models import Notification
from django.contrib.auth.models import User
from sib_api_v3_sdk import Configuration,ApiClient,TransactionalEmailsApi
from sib_api_v3_sdk.models import SendSmtpEmail
from sib_api_v3_sdk.rest import ApiException
from django.conf import settings


def inapp_notifications(recipient,type,title,content):
    Notification.objects.create(
        sender=User.objects.get(username='adminsofi'),
        recipient=recipient,
        title=title,
        content=content,
        type=type,
    )
    return 'notification sent'


def email_notifications(subject,content,recipients):
    configuration = Configuration()
    configuration.api_key['api-key'] = settings.BREVO_API_KEY

    try:
        api_client = ApiClient(configuration)  # Initialize directly
        api_instance = TransactionalEmailsApi(api_client)
        email = SendSmtpEmail(
            to=[{"email": r} for r in recipients],
            subject=subject,
            text_content=content,
            sender={"name": "Movie Hub", "email": "sofiaaa3991@gmail.com"}
        )
        api_instance.send_transac_email(email)

    except ApiException as e:
        return f"Email API failed: {e}"
    except Exception as e:
        return f"Email sending failed: {e}"

    return "Email sent."

def announcements(sender,type,title,content):
    users = User.objects.all()

    for user in users:
         Notification.objects.create(
             sender = sender,
             recipient = user,
             type = type,
             title = title,
             content = content,
         )

    return "Announcements sent"