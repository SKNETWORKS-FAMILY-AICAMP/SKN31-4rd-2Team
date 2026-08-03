from datetime import date
from django import forms
from .models import Goal, JournalEntry

class JournalEntryForm(forms.ModelForm):
    class Meta:
        model = JournalEntry
        fields = ["entry_date", "entry_type", "mood", "content"]

    def clean_content(self):
        # 앞뒤 공백 제거
        return self.cleaned_data.get("content", "").strip()

class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = ["category", "title", "target_date"]
        widgets = {
            "category": forms.TextInput(attrs={"placeholder": "예: 자격증, 체력, 어학"}),
            "title": forms.TextInput(attrs={"placeholder": "목표를 입력하세요."}),
            "target_date": forms.DateInput(attrs={"type": "date"}),
        }

    def clean_target_date(self):
        target_date = self.cleaned_data["target_date"]
        if target_date < date.today():
            raise forms.ValidationError("목표일은 오늘 이후 날짜여야 합니다.")
        return target_date