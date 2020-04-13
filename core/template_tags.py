from datetime import timedelta

from django import template
from django.utils import timezone

from core.models import Message

register = template.Library()


@register.filter()
def remaining_time(war_start_time):
    """Convert a datetime.timedelta object into Days, Hours, Minutes, Seconds."""
    timedeltaobj = war_start_time - timezone.now() + timedelta(days=1)
    secs = timedeltaobj.total_seconds()
    timetot = ""
    if secs > 86400:  # 60sec * 60min * 24hrs
        days = secs // 86400
        timetot += "{} dni".format(int(days))
        secs = secs - days * 86400

    if secs > 3600:
        hrs = secs // 3600
        timetot += " {} godziny".format(int(hrs))
        secs = secs - hrs * 3600

    if secs > 60:
        mins = secs // 60
        timetot += " {} minuty".format(int(mins))
        secs = secs - mins * 60

    if secs > 0:
        timetot += " {} sekundy".format(int(secs))
    return timetot

@register.simple_tag
def unread_messages(request):
    return Message.objects.filter(user=request.user, read=False).count()
