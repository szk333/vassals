from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from core.constants import TITLES


class User(AbstractUser):
    gold = models.PositiveIntegerField(default=0)
    last_check = models.DateTimeField(blank=True, null=True)
    points = models.PositiveIntegerField(default=50)
    liege = models.ForeignKey('self', null=True, blank=True, related_name='vassals', on_delete=models.SET_NULL)
    recruits=models.PositiveIntegerField(default=0)
    soldiers=models.PositiveIntegerField(default=0)
    def update_gold(self):
        if self.last_check:
            self.gold += ((timezone.now() - self.last_check).total_seconds() * self.income)
        self.last_check = timezone.now()
        self.save()

    @property
    def all_points(self):
        return self.points + sum([item.all_points for item in self.vassals.all()])

    @property
    def title(self):
        for title_min, name in TITLES.items():
            if self.all_points < title_min:
                return name[0]

    @property
    def income(self):
        for title_min, name in TITLES.items():
            if self.all_points < title_min:
                return name[1]


class Diplomats(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='diplomats_owner')
    number = models.IntegerField()
    destination = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE,
                                    related_name='diplomats_destination')

    def save(self, *args, **kwargs):
        if not self.destination:
            self.destination = self.owner
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Dyplomaci'
        verbose_name = 'Dyplomaci'
