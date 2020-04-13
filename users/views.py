from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Sum, F
from django.http import HttpResponse
from django.shortcuts import render, redirect

from core.constants import BASE_DIPLOMAT_COST, BASE_SOLDIER_COST
from core.models import Message
from users.forms import CustomCreationForm
from users.models import Diplomats, War, User
from users.utils import register_for_user


@login_required
def home(request):
    request.user.actions_on_login()
    current = Diplomats.objects.filter(owner=request.user).aggregate(sum=Sum('number'))['sum'] or 0
    context = {
        'current': current,
        'BASE_DIPLOMAT_COST': BASE_DIPLOMAT_COST,
        'BASE_SOLDIER_COST': BASE_SOLDIER_COST,
        'register': register_for_user(request.user),
    }

    return render(request, 'sites/home.html', context)


def signup(request):
    if request.method == 'POST':
        form = CustomCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = CustomCreationForm()
    return render(request, 'registration/signup.html', {
        'form': form
    })


@login_required
def buy_diplomats(request):
    if request.method == 'POST':
        d = Diplomats.objects.filter(owner=request.user, destination=request.user)
        if d:
            d.update(number=F('number') + request.POST['diplomats_to_buy'])
        else:
            Diplomats.objects.create(owner=request.user, number=request.POST['diplomats_to_buy'])
        request.user.gold -= int(request.POST['cost'])
        request.user.save()
    return redirect('home')


@login_required
def buy_soldiers(request):
    if request.method == 'POST':
        recruited = int(request.POST['soldiers_to_buy'])
        request.user.soldiers += recruited
        request.user.gold -= recruited * BASE_SOLDIER_COST
        request.user.recruits -= recruited
        request.user.save()
    return redirect('home')


@login_required
@transaction.atomic()
def declare_war(request):
    if request.method == 'POST':
        data = request.POST
        defender = User.objects.get(id=data['id'])
        War.objects.create(
            attacker=request.user,
            defender=defender,
            attacker_strength=data['warriors'],
            defender_strength=defender.soldiers,
            type=data['war_type']
        )
        request.user.soldiers -= int(data['warriors'])
        defender.soldiers = 0
        request.user.save()
        defender.save()
    return redirect('wars')


@login_required
def wars(request):
    context = {
        'register': register_for_user(request.user)
    }
    return render(request, 'sites/wars.html', context)


@login_required
@transaction.atomic()
def change_strength(request):
    if request.method == 'POST':
        data = request.POST
        war = War.objects.get(id=int(data.get('id')))
        amount = int(data.get('amount'))
        request.user.soldiers -= amount
        if amount < 0:
            war.add_user_strength(request.user, amount)
        else:
            war.add_user_strength(request.user, war.current_value_of_soldier * amount)
        request.user.save()
        war.save()
    return redirect('wars')

@login_required
def mailbox(request):
    context = {
        'register': register_for_user(request.user),
        'messages': Message.objects.filter(user=request.user),
    }
    return render(request, 'sites/mailbox.html', context)

@login_required
def mark_as_read(request, msg_id):
    msg = Message.objects.get(id=int(msg_id))
    msg.read = True
    msg.save()
    return HttpResponse('Msg read')
