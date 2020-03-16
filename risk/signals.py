from .models import Score
from .tasks import generate_score_task
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=Score)
def snapshot_handler(sender, instance, created, **kwargs):
    if created:
        generate_score_task.delay(instance.id)
