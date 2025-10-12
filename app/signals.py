from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def create_default_groups(sender, **kwargs):
    try:
        from django.contrib.auth.models import Group
        Group.objects.get_or_create(name='Motorista')
        Group.objects.get_or_create(name='Cliente')
        Group.objects.get_or_create(name='Admin')
    except Exception:
        pass
