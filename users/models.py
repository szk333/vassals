from django.contrib.auth.models import AbstractUser
from django.db import models, transaction
from django.utils import timezone

from core.constants import TITLES, DAILY_RECRUIT_INCOME


class User(AbstractUser):
    gold = models.PositiveIntegerField(default=0)
    last_check = models.DateTimeField(blank=True, null=True)
    points = models.PositiveIntegerField(default=50)
    liege = models.ForeignKey('self', null=True, blank=True, related_name='vassals', on_delete=models.SET_NULL)
    recruits = models.PositiveIntegerField(default=0)
    soldiers = models.PositiveIntegerField(default=0)
    last_check_date = models.DateField(blank=True, null=True)

    def update_gold(self):
        if self.last_check:
            self.gold += ((timezone.now() - self.last_check).total_seconds() * self.income)
        self.last_check = timezone.now()
        self.save()

    def update_daily(self):
        if self.last_check_date:
            self.recruits += (timezone.now().date() - self.last_check_date).days * DAILY_RECRUIT_INCOME
        self.last_check_date = timezone.now().date()
        self.save()

    def resolve_user_wars(self):
        for war in War.objects.filter(attacker=self, defender=self):
            war.resolve_war()

    def actions_on_login(self):
        with transaction.atomic():
            self.update_daily()
            self.update_gold()
            self.resolve_user_wars()

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

    def register_representation(self):
        html = f"<tr><td><h5>{self}</h5></td><td>{{}}</td></tr>"
        return html

    def __str__(self):
        return self.title + ' ' + '<b>' + self.username + '</b>'

    def get_all_lieges(self):
        if self.liege is None:
            return User.objects.none()
        return User.objects.filter(pk=self.liege.pk) | self.liege.get_all_lieges()


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


class War(models.Model):
    WAR_TYPES = [
        (0, 'Wojna wasalizacyja'),
        (1, 'Bunt'),
        (2, 'Wewnętrzna wojna o chwałę'),
        (3, 'Zewnętrzna wojna o chwałę'),
    ]
    started_at = models.DateTimeField(auto_now_add=True)
    attacker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wars_attacker')
    defender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wars_defender')
    attacker_strength = models.DecimalField(default=0, max_digits=10, decimal_places=3)
    defender_strength = models.DecimalField(default=0, max_digits=10, decimal_places=3)
    type = models.SmallIntegerField(choices=WAR_TYPES)

    def resolve_war(self):
        pass

    @staticmethod
    def existing_wars(user1, user2):
        qs = War.objects.filter(attacker=user1).filter(defender=user2)
        qs2= War.objects.filter(attacker=user2).filter(defender=user1)
        print(qs, qs2)
        return qs or qs2

    def __str__(self):
        return self.get_type_display() + ' ' + str(self.attacker) + ' vs ' + str(self.defender)
