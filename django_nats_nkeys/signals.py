# from django import dispatch
# from django.contrib.auth import get_user_model
# from django.dispatch import receiver
# from django.db.models.signals import post_save
# from .models import TurnUser, TurnAdmin
# from .services import get_or_update_turn_user

# User = get_user_model()


# @receiver(post_save, sender=User, dispatch_uid="django_coturn_user_post_save")
# def create_turn_models(sender, instance, **kwargs) -> TurnUser:
#     return get_or_update_turn_user(instance)
