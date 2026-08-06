from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import (
    ENLISTED_SERVICE_DAYS,
    OFFICER_SERVICE_DAYS,
    LoginForm,
    ProfileUpdateForm,
    SignUpForm,
)
from .models import Profile


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.POST.get('next') or reverse('home:home')
            return redirect(next_url)
    else:
        form = LoginForm(request)
    return render(request, 'account/login.html', {'form': form})


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home:home')
    else:
        form = SignUpForm()
    return render(request, 'account/signup.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home:home')


@login_required
def profile_update_view(request):
    profile = request.user.profile
    is_enlisted = profile.status == Profile.Status.ENLISTED

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, profile=profile)
        if form.is_valid():
            new_password = form.cleaned_data.get('new_password1')
            if new_password:
                request.user.set_password(new_password)
                request.user.save()
                update_session_auth_hash(request, request.user)  # 로그인 세션 유지

            new_status = form.cleaned_data['status']
            new_is_enlisted = new_status == Profile.Status.ENLISTED

            profile.status = new_status
            profile.rank = (
                form.cleaned_data.get('rank') if new_is_enlisted else form.cleaned_data.get('officer_rank')
            )

            # 신분이 바뀌면 복무기간 기준(병사/간부)도 달라지므로 전역(예정)일을 다시 계산합니다.
            service_days = ENLISTED_SERVICE_DAYS if new_is_enlisted else OFFICER_SERVICE_DAYS
            profile.discharge_date = profile.enlist_date + timedelta(days=service_days)

            profile.save()

            messages.success(request, '회원 정보가 수정되었습니다.')
            return redirect('account:update')
    else:
        initial = {'status': profile.status}
        if is_enlisted:
            initial['rank'] = profile.rank
        else:
            initial['officer_rank'] = profile.rank
        form = ProfileUpdateForm(initial=initial, profile=profile)

    return render(request, 'account/update.html', {
        'form': form,
        'profile': profile,
        'is_enlisted': is_enlisted,
    })


@login_required
@require_POST
def delete_account_view(request):
    user = request.user
    logout(request)
    user.delete()
    messages.info(request, '탈퇴가 완료되었습니다.')
    return redirect('home:home')


@login_required
def my_posts_view(request):
    posts = []
    try:
        from board.models import Post
        posts = Post.objects.filter(author=request.user).order_by('-created_at')
    except ImportError:
        posts = []
    return render(request, 'account/detail.html', {'posts': posts})