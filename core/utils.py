from django.contrib.auth import get_user_model

from core.constants import DAILY_RECRUIT_INCOME

User=get_user_model()

def get_recruits():
    for user in User.objects.all():
        user.recruits+=DAILY_RECRUIT_INCOME
        user.save()