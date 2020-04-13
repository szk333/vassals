"""vassals URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from users.views import home, signup, buy_diplomats, buy_soldiers, declare_war, wars, change_strength, mailbox, \
    mark_as_read

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup/', signup, name='signup'),
    path('buy_diplomats/', buy_diplomats, name='buy_diplomats'),
    path('buy_soldiers/', buy_soldiers, name='buy_soldiers'),
    path('declare_war/', declare_war, name='declare_war'),
    path('change_strength/', change_strength, name='change_strength'),
    path('wars/', wars, name='wars'),
    path('mailbox/', mailbox, name='mailbox'),
    path('mailbox/', mailbox, name='mailbox'),
    path('mailbox/<int:msg_id>/', mark_as_read, name='mark_as_read'),
    path('', home, name='home')
]
