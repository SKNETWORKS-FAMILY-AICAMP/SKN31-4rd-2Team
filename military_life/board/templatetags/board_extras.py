from django import template
from django.utils import timezone
from datetime import timedelta

register = template.Library()

@register.filter
def custom_timesince(value):
    """
    당일(24시간 이내) 작성된 글은 '몇 시간 전'으로 표시하고,
    24시간이 지난 글은 '날짜와 시간(h)' 형태로 표시합니다.
    """
    if not value:
        return ""
    
    now = timezone.now()
    diff = now - value

    # 24시간 이내인 경우
    if diff < timedelta(hours=24):
        hours = diff.seconds // 3600
        if hours == 0:
            return "방금 전"
        return f"{hours}시간 전"
    
    # 24시간이 지난 경우 (예: 2026.08.01 14:00)
    # timezone이 적용된 로컬 시간으로 변환
    local_value = timezone.localtime(value)
    return local_value.strftime("%Y.%m.%d %H:%M")
