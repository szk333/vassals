import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Sum
from django.utils import timezone

from core.constants import EARNINGS_PER_SECONDS


class User(AbstractUser):
    gold = models.IntegerField(default=0)
    last_check = models.DateTimeField(blank=True, null=True)
    points = models.IntegerField(default=50)
    liege=models.ForeignKey('self',null=True, blank=True, related_name='vassals', on_delete=models.SET_NULL)

    def update_gold(self):
        if self.last_check:
            self.gold += ((timezone.now() - self.last_check).total_seconds() * EARNINGS_PER_SECONDS)
        self.last_check = timezone.now()
        self.save()

    @property
    def all_points(self):
        return self.points+sum([item.all_points for item in self.vassals.all()])
