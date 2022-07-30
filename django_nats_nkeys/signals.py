# from django import dispatch
# from django.contrib.auth import get_user_model
# from django.dispatch import receiver
from django.db.models.signals import post_save, receiver

# from .models import TurnUser, TurnAdmin
# from .services import get_or_update_turn_user

# User = get_user_model()


from django_nats_nkeys.models import NatsAccount


@receiver(post_save, sender=NatsAccount, dispatch_uid="django_coturn_user_post_save")
def generate(sender, instance, **kwargs):
    return get_or_update_turn_user(instance)
