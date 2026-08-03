"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.urls import reverse

from home.views import home as home_view


def root(request):
    # If authenticated, render the home view directly; otherwise redirect to login
    if request.user.is_authenticated:
        return home_view(request)
    return redirect(reverse('account:login'))


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", root, name="root"),
    path("", include("home.urls")),
    path("account/", include("account.urls")),
    path("chatbot/", include("chatbot.urls")),
    path("records/", include("records.urls")),
    path("board/", include("board.urls")),
]
