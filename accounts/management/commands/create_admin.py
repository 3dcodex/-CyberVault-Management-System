from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Create a superuser account for testing the admin role.'

    def add_arguments(self, parser):
        parser.add_argument('--username', default='admin',    help='Superuser username (default: admin)')
        parser.add_argument('--email',    default='admin@cybervault.local', help='Superuser email')
        parser.add_argument('--password', default='Admin@CyberVault1', help='Superuser password')

    def handle(self, *args, **options):
        username = options['username']
        email    = options['email']
        password = options['password']

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(
                f'Superuser "{username}" already exists — skipping creation.'
            ))
            self.stdout.write(f'  Login at: http://127.0.0.1:8000/accounts/login/')
            self.stdout.write(f'  Django admin: http://127.0.0.1:8000/admin/')
            return

        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )

        self.stdout.write(self.style.SUCCESS(f'Superuser created successfully.'))
        self.stdout.write(f'  Username : {user.username}')
        self.stdout.write(f'  Email    : {user.email}')
        self.stdout.write(f'  Password : {password}')
        self.stdout.write(f'  Login at : http://127.0.0.1:8000/accounts/login/')
        self.stdout.write(f'  Admin at : http://127.0.0.1:8000/admin/')
