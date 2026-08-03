import calendar as cal_module
from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import GoalForm, JournalEntryForm
from .models import Goal, JournalEntry

# 일정 유형별 아이콘 (캘린더 화면에 표시)
TYPE_EMOJI = {
    "일반": "✏️",
    "휴가": "🏖️",
    "외박": "🏠",
    "외출": "🚶",
}


@login_required
def records(request):
    if request.method == "POST":
        return _handle_post(request)

    today = date.today()
    context = {"active_tab": request.GET.get("tab", "dday")}
    context.update(_get_dday_context(request, today))
    context.update(_get_calendar_context(request, today))
    context.update(_get_goals_context(request))
    return render(request, "records/records.html", context)


def _handle_post(request):
    """PRG 패턴: 저장 후 같은 탭으로 리다이렉트"""
    form_type = request.POST.get("form_type")

    if form_type == "journal":
        form = JournalEntryForm(request.POST)
        if form.is_valid():
            entry_date = form.cleaned_data["entry_date"]
            # 같은 날짜에 이미 기록이 있으면 덮어쓰기
            JournalEntry.objects.update_or_create(
                user=request.user,
                entry_date=entry_date,
                defaults={
                    "entry_type": form.cleaned_data["entry_type"],
                    "mood": form.cleaned_data["mood"],
                    "content": form.cleaned_data["content"],
                },
            )
            messages.success(request, "일정이 저장되었습니다.")
            return redirect(
                f"{request.path}?tab=calendar&year={entry_date.year}&month={entry_date.month}"
            )
        messages.error(request, "일정을 저장하지 못했습니다. 입력값을 확인해주세요.")
        return redirect(f"{request.path}?tab=calendar")

    if form_type == "goal":
        form = GoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            messages.success(request, "목표가 추가되었습니다.")
        else:
            messages.error(request, "목표를 추가하지 못했습니다. 입력값을 확인해주세요.")
        return redirect(f"{request.path}?tab=goals")

    return redirect(request.path)


def _get_dday_context(request, today):
    profile = getattr(request.user, "profile", None)
    if not profile or not profile.enlist_date or not profile.discharge_date:
        return {"service_info": None}

    total_days = (profile.discharge_date - profile.enlist_date).days
    served_days = (today - profile.enlist_date).days
    remaining_days = (profile.discharge_date - today).days

    progress_percent = 0
    if total_days > 0:
        progress_percent = min(100, max(0, round(served_days / total_days * 100)))

    return {
        "service_info": profile,
        "served_days": max(served_days, 0),
        "total_days": total_days,
        "remaining_days": remaining_days,
        "progress_percent": progress_percent,
    }


def _get_calendar_context(request, today):
    year = int(request.GET.get("year", today.year))
    month = int(request.GET.get("month", today.month))

    entries = JournalEntry.objects.filter(
        user=request.user, entry_date__year=year, entry_date__month=month
    )
    entries_by_day = {entry.entry_date.day: entry for entry in entries}

    # 목표 마감일이 이번 달에 있으면 캘린더에 같이 표시
    goals_this_month = Goal.objects.filter(
        user=request.user, target_date__year=year, target_date__month=month
    )
    goals_by_day = {goal.target_date.day: goal for goal in goals_this_month}

    weeks = []
    calendar_gen = cal_module.Calendar(firstweekday=6)  # 일요일부터 시작
    for week in calendar_gen.monthdayscalendar(year, month):
        week_data = []
        for day in week:
            if day == 0:
                week_data.append(None)
                continue

            entry = entries_by_day.get(day)
            goal = goals_by_day.get(day)
            week_data.append(
                {
                    "day": day,
                    "entry_type": entry.entry_type if entry else "",
                    "mood": entry.mood if entry else "",
                    "content": entry.content if entry else "",
                    "entry_emoji": TYPE_EMOJI.get(entry.entry_type, "") if entry else "",
                    "goal_category": goal.category if goal else "",
                    "is_today": (
                        year == today.year and month == today.month and day == today.day
                    ),
                }
            )
        weeks.append(week_data)

    prev_month = 12 if month == 1 else month - 1
    prev_year = year - 1 if month == 1 else year
    next_month = 1 if month == 12 else month + 1
    next_year = year + 1 if month == 12 else year

    return {
        "year": year,
        "month": month,
        "weeks": weeks,
        "overnight_count": entries.filter(
            entry_type=JournalEntry.EntryType.OVERNIGHT
        ).count(),
        "prev_year": prev_year,
        "prev_month": prev_month,
        "next_year": next_year,
        "next_month": next_month,
    }


def _get_goals_context(request):
    goals = Goal.objects.filter(user=request.user).order_by("is_done", "target_date")
    return {
        "goals": goals,
        "goal_form": GoalForm(),
    }