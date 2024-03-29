from django.core.management.base import BaseCommand

# Import user model
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Create superuser nhien/1234'

    def handle(self, *args, **options):
        if not User.objects.filter(username='nhien').exists():
            User.objects.create_superuser('nhien', 'nhien@moneyshank.co', '1234')
            self.stdout.write(self.style.SUCCESS('Superuser created successfully!'))
        else:
            self.stdout.write(self.style.NOTICE('Superuser already exists!'))