from datetime import timedelta

from django.db import models
from django.utils import timezone


class WarManager(models.Manager):
    def get_queryset(self, statuses=[0]):
        return super().get_queryset().filter(status__in=statuses)

    def finished(self):
        return self.get_queryset().filter(started_at__lt=(timezone.now() - timedelta(days=1)))
