from datetime import timedelta

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model

from .models import Profile

# Profile.rank는 모델에 choices가 없는 자유 입력 CharField라서,
# 계급 버튼 목록은 여기서만 정의합니다.
ENLISTED_RANK_CHOICES = [
    ('이병', '이병'),
    ('일병', '일병'),
    ('상병', '상병'),
    ('병장', '병장'),
]

# 간부 계급은 부사관/장교 그룹으로 나눠서 버튼으로 선택합니다.
OFFICER_RANK_CHOICES = [
    ('부사관', [
        ('하사', '하사'),
        ('중사', '중사'),
        ('상사', '상사'),
        ('원사', '원사'),
        ('준위', '준위'),
    ]),
    ('장교', [
        ('소위', '소위'),
        ('중위', '중위'),
        ('대위', '대위'),
        ('소령', '소령'),
        ('중령', '중령'),
        ('대령', '대령'),
    ]),
]

# TODO: 전역(예정)일 계산 기준(복무기간)은 실제 정책/군종에 맞게 조정 필요.
# 현재: 병사 18개월(548일), 간부 임시로 36개월(1095일) 기준.
ENLISTED_SERVICE_DAYS = 548
OFFICER_SERVICE_DAYS = 1095

class LoginForm(AuthenticationForm):
    """디자인 시안(플레이스홀더 문구)에 맞춘 로그인 폼"""
    username = forms.CharField(
        label='아이디',
        widget=forms.TextInput(attrs={
            'placeholder': '아이디를 입력하세요',
            'autofocus': True,
        }),
    )
    password = forms.CharField(
        label='비밀번호',
        widget=forms.PasswordInput(attrs={
            'placeholder': '비밀번호를 입력하세요',
        }),
    )


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    enlist_date = forms.DateField(
        label='입대일',
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    status = forms.ChoiceField(
        label='신분',
        choices=Profile.Status.choices,
        initial=Profile.Status.ENLISTED,
        widget=forms.RadioSelect,
    )
    rank = forms.ChoiceField(
        label='계급',
        choices=ENLISTED_RANK_CHOICES,
        required=False,
        widget=forms.RadioSelect,
    )
    officer_rank = forms.ChoiceField(
        label='계급',
        choices=OFFICER_RANK_CHOICES,
        required=False,
        widget=forms.RadioSelect,
    )

    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'placeholder': '사용할 아이디를 입력하세요'})
        self.fields['email'].widget.attrs.update({'placeholder': '이메일을 입력하세요'})
        self.fields['password1'].widget.attrs.update({'placeholder': '비밀번호를 입력하세요'})
        self.fields['password2'].widget.attrs.update({'placeholder': '비밀번호를 다시 입력하세요'})

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        rank = cleaned_data.get('rank')
        officer_rank = cleaned_data.get('officer_rank')

        if status == Profile.Status.ENLISTED and not rank:
            self.add_error('rank', '계급을 선택해 주세요.')
        if status == Profile.Status.OFFICER and not officer_rank:
            self.add_error('officer_rank', '계급을 입력해 주세요.')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()

            status = self.cleaned_data['status']
            enlist_date = self.cleaned_data['enlist_date']
            rank = (
                self.cleaned_data.get('rank')
                if status == Profile.Status.ENLISTED
                else self.cleaned_data.get('officer_rank')
            )
            service_days = (
                ENLISTED_SERVICE_DAYS if status == Profile.Status.ENLISTED else OFFICER_SERVICE_DAYS
            )
            discharge_date = enlist_date + timedelta(days=service_days)

            Profile.objects.create(
                user=user,
                status=status,
                rank=rank,
                enlist_date=enlist_date,
                discharge_date=discharge_date,
            )
        return user


class ProfileUpdateForm(forms.Form):
    """회원 정보 수정 폼. 아이디/신분(status)은 변경 불가(화면에 표시만), 계급(rank)만 수정 가능."""
    new_password1 = forms.CharField(
        label='새 비밀번호',
        required=False,
        widget=forms.PasswordInput(attrs={'placeholder': '변경할 경우에만 입력'}),
    )
    new_password2 = forms.CharField(
        label='비밀번호 확인',
        required=False,
        widget=forms.PasswordInput(attrs={'placeholder': '비밀번호 재입력'}),
    )
    rank = forms.ChoiceField(
        label='계급',
        choices=ENLISTED_RANK_CHOICES,
        required=False,
        widget=forms.RadioSelect,
    )
    officer_rank = forms.ChoiceField(
        label='계급',
        choices=OFFICER_RANK_CHOICES,
        required=False,
        widget=forms.RadioSelect,
    )

    def __init__(self, *args, profile=None, **kwargs):
        self.profile = profile
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        pw1 = cleaned_data.get('new_password1')
        pw2 = cleaned_data.get('new_password2')
        if pw1 or pw2:
            if pw1 != pw2:
                raise forms.ValidationError('비밀번호가 일치하지 않습니다.')
            if len(pw1) < 8:
                raise forms.ValidationError('비밀번호는 8자 이상이어야 합니다.')

        if self.profile and self.profile.status == Profile.Status.ENLISTED:
            if not cleaned_data.get('rank'):
                self.add_error('rank', '계급을 선택해 주세요.')
        else:
            if not cleaned_data.get('officer_rank'):
                self.add_error('officer_rank', '계급을 입력해 주세요.')
        return cleaned_data