from django.shortcuts import render
from datetime import date

from account.models import Profile


def home(request):
    ddays = None
    discharge_date = None
    progress_percent = None
    # If user has profile with enlist/discharge dates, compute D-day and progress
    if request.user.is_authenticated:
        try:
            profile = Profile.objects.get(user=request.user)
            discharge_date = profile.discharge_date
            enlist_date = profile.enlist_date
            today = date.today()
            total_days = (discharge_date - enlist_date).days if discharge_date and enlist_date else None
            days_left = (discharge_date - today).days if discharge_date else None
            if days_left is not None:
                ddays = days_left
            if total_days and total_days > 0 and days_left is not None:
                progress_percent = max(0, min(100, int((total_days - days_left) / total_days * 100)))
        except Profile.DoesNotExist:
            pass

    # Fallback sample values for anonymous users
    if ddays is None:
        ddays = 47
        discharge_date = None
        progress_percent = 91

    return render(request, "home/index.html", {
        'ddays': ddays,
        'discharge_date': discharge_date,
        'progress_percent': progress_percent,
    })
