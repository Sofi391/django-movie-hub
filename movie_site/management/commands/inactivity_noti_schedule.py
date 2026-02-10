from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, CrontabSchedule
import json
from movie_site.tasks import inactive_users_notification

class Command(BaseCommand):
    help = 'Set up daily interaction email task'

    def handle(self, *args, **options):
        schedule, _ = CrontabSchedule.objects.get_or_create(
            minute='0',
            hour='0',
        )
        task, created = PeriodicTask.objects.get_or_create(
            crontab=schedule,
            name='Daily inactive user email',
            task='movie_site.tasks.inactive_users_notification',
            defaults={'args': json.dumps([])}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Interaction notifications task created'))
        else:
            self.stdout.write('Task already exists')
