from apscheduler.schedulers.blocking import BlockingScheduler
from django.contrib.auth import get_user_model

from core.constants import DAILY_RECRUIT_INCOME

User = get_user_model()
sched = BlockingScheduler()


@sched.scheduled_job('interval', minutes=5)
def get_recruits():
    for user in User.objects.all():
        user.recruits += DAILY_RECRUIT_INCOME
        user.save()


sched.start()
