from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Create demo users for testing'

    def handle(self, *args, **options):
        # Create admin user
        admin_user, created = User.objects.get_or_create(
            email='admin@example.com',
            defaults={
                'username': 'admin',
                'name': 'System Administrator',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(
                self.style.SUCCESS('Created admin user: admin@example.com / admin123')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Admin user already exists')
            )

        # Create investigator user
        investigator_user, created = User.objects.get_or_create(
            email='investigator@example.com',
            defaults={
                'username': 'investigator',
                'name': 'John Investigator',
                'role': 'investigator',
            }
        )
        if created:
            investigator_user.set_password('investigator123')
            investigator_user.save()
            self.stdout.write(
                self.style.SUCCESS('Created investigator user: investigator@example.com / investigator123')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Investigator user already exists')
            )

        # Create regulator user
        regulator_user, created = User.objects.get_or_create(
            email='regulator@example.com',
            defaults={
                'username': 'regulator',
                'name': 'Jane Regulator',
                'role': 'regulator',
            }
        )
        if created:
            regulator_user.set_password('regulator123')
            regulator_user.save()
            self.stdout.write(
                self.style.SUCCESS('Created regulator user: regulator@example.com / regulator123')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Regulator user already exists')
            )

        self.stdout.write(
            self.style.SUCCESS('Demo users setup completed!')
        )
