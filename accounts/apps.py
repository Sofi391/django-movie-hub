from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        # Auto-create superuser
        from django.contrib.auth import get_user_model
        User = get_user_model()

        # Fetch credentials from environment variables or use defaults
        username = "adminsofi"
        email = "sofiaaa3991@gmail.com"
        password = "@sofidid123"

        # Only create if it doesn't exist
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username, email=email, password=password)
            print(f"Superuser '{username}' created successfully!")