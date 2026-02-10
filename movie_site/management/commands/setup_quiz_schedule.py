from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, CrontabSchedule
import json
from movie_site.tasks import weekly_rotation

class Command(BaseCommand):
    help = 'Set up weekly rotation task'

    def handle(self, *args, **options):
        schedule, _ = CrontabSchedule.objects.get_or_create(
            minute='0',
            hour='0',
            day_of_week='6',
        )
        task, created = PeriodicTask.objects.get_or_create(
            crontab=schedule,
            name='Weekly quiz rotation',
            task='movie_site.tasks.weekly_rotation',
            defaults={'args': json.dumps([])}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Weekly rotation task created'))
        else:
            self.stdout.write('Task already exists')
