# users/management/commands/seed_users.py
from django.core.management.base import BaseCommand
from accounts.models import User
from django.contrib.auth.models import Group


class Command(BaseCommand):
    help = "Seed default users and assign them to groups"

    def handle(self, *args, **kwargs):
        # SuperAdmin user
        superadmin, created = User.objects.get_or_create(
            email="superadmin@example.com",
            defaults={
                "full_name": "superadmin",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            superadmin.set_password("superadmin123")
            superadmin.save()
            superadmin.groups.add(Group.objects.get(name="SuperAdmin"))
            self.stdout.write(self.style.SUCCESS("✔ Created SuperAdmin user"))
        else:
            self.stdout.write(self.style.WARNING("• SuperAdmin user already exists"))

        # Sales user
        sales, created = User.objects.get_or_create(
            email="sales@example.com",
            defaults={"full_name": "sales", "is_staff": False, "is_superuser": False},
        )
        if created:
            sales.set_password("sales123")
            sales.save()
            sales.groups.add(Group.objects.get(name="Sales"))
            self.stdout.write(self.style.SUCCESS("✔ Created Sales user"))
        else:
            self.stdout.write(self.style.WARNING("• Sales user already exists"))

        # Designer user
        designer, created = User.objects.get_or_create(
            email="designer@example.com",
            defaults={
                "full_name": "designer",
                "is_staff": False,
                "is_superuser": False,
            },
        )
        if created:
            designer.set_password("designer123")
            designer.save()
            designer.groups.add(Group.objects.get(name="Designer"))
            self.stdout.write(self.style.SUCCESS("✔ Created Designer user"))
        else:
            self.stdout.write(self.style.WARNING("• Designer user already exists"))

        self.stdout.write(self.style.SUCCESS("\n✅ Users seeding complete!"))
