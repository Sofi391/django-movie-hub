from celery import shared_task
from celery.exceptions import MaxRetriesExceededError
from celery.signals import task_postrun
from .models import Question
from django.contrib.auth.models import User
from .services import inapp_notifications,email_notifications
from django.utils import timezone
from django.db.models import Max
from django.db import connections


@task_postrun.connect
def close_db_connection(*args, **kwargs):
    for conn in connections.all():
        conn.close()


@shared_task
def weekly_rotation():
    Question.objects.update(is_active=False)

    weekly_ids = list(
        Question.objects.order_by('?')[:100]
        .values_list('id', flat=True)
    )

    Question.objects.filter(id__in=weekly_ids).update(is_active=True)

    return "Weekly quiz rotation completed."


@shared_task
def weekly_notification():
    users = User.objects.all()
    type_info = 'Quiz'
    title = "Weekly Quiz & Movie Update 🎉"
    content = f"""
Your weekly dose of quizzes and movie updates are here! 

Check out the latest quizzes, explore new movies, and keep earning badges. 

Visit Home > Quizzes to start your weekly challenge! 🎬
    """

    for user in users:
        inapp_notifications(user,type_info,title,content)

    return "Weekly notification sent."



@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_email_task(self, subject, content, recipients):
    """retry up to 3 times, 1 min delay"""
    try:
        result = email_notifications(subject, content, recipients)
        return result
    except Exception as exc:
        try:
            self.retry(exc=exc)
        except MaxRetriesExceededError:
            print(f"Email to {recipients} failed after 3 retries.")


THRESHOLD = {15,30,45,90}
@shared_task
def inactive_users_notification():
    now = timezone.now().date()
    users = User.objects.filter(last_login__isnull = False)

    for user in users:
        inactivity_days = (now - user.last_login.date()).days
        if inactivity_days in THRESHOLD:
            subject = f'Hi {user.username}, quick update from Movie Hub'
            content = f"""
Hi {user.username},

We noticed you haven’t visited Movie Hub in a while, so we wanted to give you a quick update.

There are new quizzes available and your progress is saved, ready for you whenever you come back.

You can continue where you left off here:
https://movie-hub-a4gn.onrender.com/

See you soon,
Movie Hub
"""
            recipient_list = [user.email]
            send_email_task.delay(subject,content,recipient_list)

    return "notifications for inactive users sent."



@shared_task
def inactive_badge():
    now = timezone.now().date()
    users = User.objects.annotate(
        latest_date_awarded = Max('badges__awarded_at')
    ).filter(latest_date_awarded__isnull=False)

    for user in users:
        unearned_days = (now-user.latest_date_awarded.date()).days
        if unearned_days in THRESHOLD:
            subject = 'Update on your Movie Hub progress'
            content = f"""
Hi {user.username},

We wanted to let you know that it’s been a while since your last badge activity on Movie Hub.

Your progress is still saved, and quizzes are available whenever you’re ready to continue.

You can check your profile and continue here:
https://movie-hub-a4gn.onrender.com/

Best regards,
Movie Hub
"""
            recipient_list = [user.email]
            send_email_task.delay(subject, content, recipient_list)

    return "notifications for inactive badges sent."

