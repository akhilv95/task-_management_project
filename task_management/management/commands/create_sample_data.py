from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from datetime import timedelta
from django.utils import timezone

User = get_user_model()

class Command(BaseCommand):
    help = 'Create sample data for testing'

    def handle(self, *args, **options):
        # Create SuperAdmin
        if not User.objects.filter(username='superadmin').exists():
            User.objects.create_user(
                username='superadmin',
                email='super@admin.com',
                password='admin123',
                role='superadmin'
            )
            self.stdout.write('Created SuperAdmin: superadmin/admin123')

        # Create Admin
        if not User.objects.filter(username='admin1').exists():
            User.objects.create_user(
                username='admin1',
                email='admin@test.com',
                password='admin123',
                role='admin'
            )
            self.stdout.write('Created Admin: admin1/admin123')

        # Create User
        if not User.objects.filter(username='user1').exists():
            User.objects.create_user(
                username='user1',
                email='user@test.com',
                password='user123',
                role='user'
            )
            self.stdout.write('Created User: user1/user123')

        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))