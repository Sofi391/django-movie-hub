from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, CrontabSchedule
import json
from movie_site.tasks import inactive_badge

class Command(BaseCommand):
    help = 'Set up daily badge email task'

    def handle(self, *args, **options):
        schedule, _ = CrontabSchedule.objects.get_or_create(
            minute='0',
            hour='0',
            day_of_week='*',
            day_of_month='*',
            month_of_year='*',
        )
        task, created = PeriodicTask.objects.get_or_create(
            crontab=schedule,
            name='Daily badge activity email',
            task='movie_site.tasks.inactive_badge',
            defaults={'args': json.dumps([])}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Badge activity notifications task created'))
        else:
            self.stdout.write('Task already exists')
