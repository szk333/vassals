from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import AbstractUser
from django.db import models, transaction
from django.utils import timezone

from core.constants import TITLES, DAILY_RECRUIT_INCOME
from users.managers import WarManager


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
        for war in War.objects.finished():  # maybe fiter it later
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
    STATUSES = [
        (0, 'Aktywna'),
        (1, 'Zakończona'),
    ]
    started_at = models.DateTimeField(auto_now_add=True)
    started_at.editable = True  # for admin site
    attacker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wars_attacker')
    defender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wars_defender')
    attacker_strength = models.DecimalField(default=0, max_digits=10, decimal_places=3)
    defender_strength = models.DecimalField(default=0, max_digits=10, decimal_places=3)
    type = models.SmallIntegerField(choices=WAR_TYPES)
    status = models.SmallIntegerField(choices=STATUSES, default=0)
    objects = WarManager()

    @transaction.atomic
    def resolve_war(self):
        from core.models import Message

        if self.attacker_strength > self.defender_strength:
            winner = self.attacker
            looser = self.defender
            if self.type == 0:  # vasalize defender
                looser.liege = winner
            if self.type == 1:  # unvasalize atacker
                winner.liege = None
            if self.type in [2, 3]:
                points = round(looser.points * 0.2)
                looser.points -= points
                winner.points += points
        else:
            winner = self.defender
            looser = self.attacker
            if self.type == 0:  # transfer points
                points = round(looser.points * 0.4)
                looser.points -= points
                winner.points += points
            if self.type == 1:  # unvasalize atacker
                points = round(looser.points * 0.2)
                looser.points -= points
                winner.points += points
                Diplomats.objects.update_or_create(owner=looser, destination=winner, defaults={'number': 0})
            if self.type in [2, 3]:
                points = round(looser.points * 0.4)
                looser.points -= points
                winner.points += points

        Message.objects.create(user=winner, title="Wygrałeś wojnę", text=f"Wygrałeś wojnę {self}")
        Message.objects.create(user=looser, title="Przegrałeś wojnę", text=f"Przegrałeś wojnę {self}")

        # calculate loses
        str_sum = self.attacker_strength + self.defender_strength
        self.attacker.soldiers += (self.attacker_strength * self.attacker_strength / str_sum)
        self.defender.soldiers += (self.defender_strength * self.defender_strength / str_sum)

        self.status = 1
        self.save()
        looser.save()
        winner.save()

    @staticmethod
    def existing_wars(user1, user2):
        qs = War.objects.filter(attacker=user1).filter(defender=user2)
        qs2 = War.objects.filter(attacker=user2).filter(defender=user1)
        return qs or qs2

    def add_user_strength(self, user, value):
        value = Decimal(str(value))
        if user == self.attacker:
            self.attacker_strength += value
        elif user == self.defender:
            self.defender_strength += value
        self.save()

    @property
    def current_value_of_soldier(self):
        return (self.started_at - timezone.now() + timedelta(days=1)).total_seconds() / (24 * 3600)

    def __str__(self):
        return self.get_type_display() + ' ' + str(self.attacker) + ' vs ' + str(self.defender)
