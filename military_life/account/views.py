from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import LoginForm, ProfileUpdateForm, SignUpForm
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

            profile.rank = (
                form.cleaned_data.get('rank') if is_enlisted else form.cleaned_data.get('officer_rank')
            )
            profile.save()

            messages.success(request, '회원 정보가 수정되었습니다.')
            return redirect('account:update')
    else:
        initial = {'rank': profile.rank} if is_enlisted else {'officer_rank': profile.rank}
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
    """
    내가 쓴 게시글 목록.
    TODO(board팀): board.models.Post의 실제 필드/related_name이 확정되면
    아래 쿼리와 detail.html의 post.postlike_set / post.comment_set 부분을
    실제 모델 구조에 맞게 조정해 주세요.
    """
    posts = []
    try:
        from board.models import Post
        posts = Post.objects.filter(author=request.user).order_by('-created_at')
    except ImportError:
        posts = []
    return render(request, 'account/detail.html', {'posts': posts})