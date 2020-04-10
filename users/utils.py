from users.models import User, War
from django.urls import reverse


def register_for_user(user):
    html = ''
    RIOT = "<label><input class='with-gap' type='radio' checked name='war_type' value='1'/><span>Bunt</span></label>"
    VASSALIZE = "<label><input class='with-gap' type='radio' checked name='war_type' value='0'/><span>Wasalizuj</span></label>"
    EXTERNAL = "<label><input class='with-gap' type='radio' checked name='war_type' value='3'/><span>Wojna o honor</span></label>"
    INTERNAL = "<label><input class='with-gap' type='radio' checked name='war_type' value='2'/><span>Wojna o honor</span></label>"
    WARRIORS = f"<input type='number' name='warriors' placeholder='żołnierze' max='{user.soldiers}'/>"
    BUTTON = f"<button type='submit' class='btn btn-primary'>Wyślij wojsko</button>"
    if user.liege:
        html += '<tr><td colspan="2" class="table_header">Senior</td></tr>'
        disabled = 'disabled' if War.existing_wars(user, user.liege) else ''
        war_action = f"<button class='btn register waves-effect waves-light {disabled}' onclick=war_form({user.liege.id})>" \
                     f"<i class='ra ra-crossed-axes'></i></button>"
        war_form = f"<tr id='war{user.liege.id}' class='war_form' style='display:none;'><td colspan='2'>" \
                   f"<form method='post' action='{reverse('declare_war')}'><div class='row'>" \
                   f"<div class='input-field col s6'>{RIOT}</div>" \
                   f"<div class='input-field col s3'>{WARRIORS}</div>" \
                   f"<div class='input-field col s3'>{BUTTON}</div>" \
                   f"<input type='hidden' name='id' value='{user.liege.id}'>" \
                   f"</div></form></td></tr>"
        html += user.liege.register_representation().format(war_action)
        html += war_form
    vassals = User.objects.filter(liege=user)

    if vassals:
        html += '<tr><td colspan="2" class="table_header">Wasalowie</td></tr>'
    for vassal in vassals:
        war_action = f"<button class='btn register disabled waves-effect waves-light' onclick=war_form({vassal.id})>" \
                     f"<i class='ra ra-crossed-axes'></i></button>"
        html += vassal.register_representation().format(war_action)

    independents = User.objects.filter(liege__isnull=True).exclude(id=user.id).difference(user.get_all_lieges())
    vassals_of_user_liege = User.objects.filter(liege=user.liege).exclude(id=user.id).difference(independents)
    if vassals_of_user_liege:
        html += '<tr><td colspan="2" class="table_header">Wasale mojego seniora</td></tr>'
    for liege_vassal in vassals_of_user_liege:
        disabled = 'disabled' if War.existing_wars(user, liege_vassal) else ''
        war_action = f"<button class='btn register {disabled} waves-effect waves-light' onclick=war_form({liege_vassal.id})>" \
                     f"<i class='ra ra-crossed-axes'></i></button>"
        internal = INTERNAL if not user.income > liege_vassal.income else ''

        war_form = f"<tr id='war{liege_vassal.id}' class='war_form' style='display:none;'><td colspan='2'>" \
                   f"<form method='post' action='{reverse('declare_war')}'><div class='row'>" \
                   f"<div class='input-field col s3'>{VASSALIZE}</div>" \
                   f"<div class='input-field col s3'>{internal}</div>" \
                   f"<div class='input-field col s3'>{WARRIORS}</div>" \
                   f"<div class='input-field col s3'>{BUTTON}</div>" \
                   f"<input type='hidden' name='id' value='{liege_vassal.id}'>" \
                   f"</div></form></td></tr>"
        html += liege_vassal.register_representation().format(war_action)
        html += war_form
    if independents:
        html += '<tr><td colspan="2" class="table_header">Niepodlegli</td></tr>'
    for independent in independents:
        disabled = 'disabled' if War.existing_wars(user, independent) else ''

        war_action = f"<button class='btn register waves-effect waves-light {disabled}' onclick=war_form({independent.id})>" \
                     f"<i class='ra ra-crossed-axes'></i></button>"
        external = EXTERNAL if not user.liege and not user.income > independent.income else ''

        war_form = f"<tr id='war{independent.id}' class='war_form' style='display:none;'><td colspan='2'>" \
                   f"<form method='post' action='{reverse('declare_war')}'><div class='row'>" \
                   f"<div class='input-field col s3'>{VASSALIZE}</div>" \
                   f"<div class='input-field col s3'>{external}</div>" \
                   f"<div class='input-field col s3'>{WARRIORS}</div>" \
                   f"<div class='input-field col s3'>{BUTTON}</div>" \
                   f"<input type='hidden' name='id' value='{independent.id}'>" \
                   f"</div></form></td></tr>"
        html += independent.register_representation().format(war_action)
        html += war_form
    return html

