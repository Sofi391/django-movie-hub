from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Create superuser if not exists'

    def handle(self, *args, **kwargs):
        if not User.objects.filter(username='adminsofi').exists():
            User.objects.create_superuser('adminsofi','sofiaaa3991@gmail.com','@sofidid123')
            self.stdout.write('Superuser created')
        else:
            self.stdout.write('Superuser already exists')
