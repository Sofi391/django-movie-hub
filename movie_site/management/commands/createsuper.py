from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = "Create a superuser if not exists"

    def handle(self, *args, **kwargs):
        User = get_user_model()
        if not User.objects.filter(username="adminsofi").exists():
            User.objects.create_superuser(
                username="adminsofi",
                email="sofiaaa3991@gmail.com",
                password="@sofidid123"
            )
            self.stdout.write(self.style.SUCCESS("Superuser created!"))
        else:
            self.stdout.write(self.style.WARNING("Superuser already exists"))
