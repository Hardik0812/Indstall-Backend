from django.apps import apps
from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_migrate
from django.dispatch import receiver

DEFAULT_GROUPS = ["Admin", "Sales", "Designer"]

@receiver(post_migrate)
def create_default_groups(sender, **kwargs):
    # Only run after auth & our app are ready
    if sender.name not in {"accounts", "django.contrib.auth"}:
        return

    # Ensure groups exist
    for name in DEFAULT_GROUPS:
        Group.objects.get_or_create(name=name)

    # (Optional) Example: give Admin all permissions
    try:
        admin_group = Group.objects.get(name="Admin")
        admin_group.permissions.set(Permission.objects.all())
    except Group.DoesNotExist:
        pass
