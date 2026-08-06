from django.shortcuts import render
from django.utils import timezone

from account.models import Profile


def home(request):
    ddays = None
    discharge_date = None
    progress_percent = None
    is_officer_without_dday = False

    if request.user.is_authenticated:
        try:
            profile = Profile.objects.get(user=request.user)
            discharge_date = profile.discharge_date
            enlist_date = profile.enlist_date
            today = timezone.localdate()  # 서버 UTC가 아니라 TIME_ZONE(Asia/Seoul) 기준 오늘

            if discharge_date and enlist_date:
                total_days = (discharge_date - enlist_date).days
                days_left = (discharge_date - today).days
                ddays = days_left
                if total_days > 0:
                    progress_percent = max(0, min(100, int((total_days - days_left) / total_days * 100)))
            else:
                is_officer_without_dday = True

        except Profile.DoesNotExist:
            pass
    else:
        ddays = 47
        progress_percent = 91

    # D-day 표시 문자열을 여기서 미리 만들어서 템플릿은 단순하게 유지
    if ddays is not None:
        dday_label = f"D-{ddays}" if ddays >= 0 else f"D+{abs(ddays)}"
    else:
        dday_label = None

    return render(request, "home/index.html", {
        'ddays': ddays,
        'dday_label': dday_label,
        'discharge_date': discharge_date,
        'progress_percent': progress_percent,
        'is_officer_without_dday': is_officer_without_dday,
    })