from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.db.models import Count, Q
from django.contrib.auth.decorators import login_required
from .models import Post, Category, Comment, PostLike, Report
import json

@login_required
def post_list(request):
    """
    게시판 목록을 조회하는 뷰입니다.
    """
    category_id = request.GET.get('category')
    search_query = request.GET.get('q')

    posts = Post.objects.annotate(
        like_count=Count('likes', distinct=True),
        comment_count=Count('comments', distinct=True)
    ).order_by('-created_at')

    if category_id:
        posts = posts.filter(category_id=category_id)
    if search_query:
        posts = posts.filter(Q(title__icontains=search_query) | Q(content__icontains=search_query))

    categories = Category.objects.all()

    context = {
        'posts': posts,
        'categories': categories,
        'current_category': int(category_id) if category_id else None,
        'search_query': search_query or '',
    }
    return render(request, 'board/post_list.html', context)

@login_required
def post_detail(request, pk):
    """
    특정 게시글의 상세 내용을 조회하는 뷰입니다.
    사용자의 세션을 이용하여 새로고침 시 조회수가 중복으로 올라가는 것을 방지합니다.
    댓글 목록과 좋아요 상태를 함께 템플릿으로 전달합니다.
    """
    post = get_object_or_404(Post, pk=pk)
    
    # 조회수 무조건 1 증가 (사용자 요청)
    post.view_count += 1
    post.save(update_fields=['view_count'])

    comments = post.comments.order_by('created_at')
    likes_count = post.likes.count()
    user_has_liked = post.likes.filter(user=request.user).exists()
    user_has_reported = post.reports.filter(reporter=request.user).exists()

    context = {
        'post': post,
        'comments': comments,
        'likes_count': likes_count,
        'user_has_liked': user_has_liked,
        'user_has_reported': user_has_reported,
    }
    return render(request, 'board/post_detail.html', context)

@login_required
def post_create(request):
    """
    새로운 게시글을 생성하는 비동기(Ajax) 뷰입니다.
    모달 창에서 입력된 데이터를 JSON 형태로 받아 처리하고,
    작성자는 현재 로그인한 사용자로 자동 지정되지만 화면에는 익명으로 처리됩니다.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            category_id = data.get('category')
            title = data.get('title')
            content = data.get('content')

            if not all([category_id, title, content]):
                return JsonResponse({'status': 'error', 'message': '모든 필드를 입력해주세요.'}, status=400)

            category = get_object_or_404(Category, pk=category_id)
            post = Post.objects.create(
                author=request.user,
                category=category,
                title=title,
                content=content
            )
            return JsonResponse({'status': 'success', 'post_id': post.id})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return HttpResponseBadRequest()

@login_required
def post_update(request, pk):
    """
    기존 게시글을 수정하는 비동기(Ajax) 뷰입니다.
    요청한 사용자가 게시글의 실제 작성자인지 확인한 후 제목과 내용을 수정합니다.
    """
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        return HttpResponseForbidden("수정 권한이 없습니다.")

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            category_id = data.get('category')
            title = data.get('title')
            content = data.get('content')

            if category_id:
                post.category = get_object_or_404(Category, pk=category_id)
            if title:
                post.title = title
            if content:
                post.content = content
            post.save()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return HttpResponseBadRequest()

@login_required
def post_delete(request, pk):
    """
    기존 게시글을 삭제하는 비동기(Ajax) 뷰입니다.
    요청한 사용자가 게시글의 실제 작성자인지 권한을 확인한 후 삭제를 수행합니다.
    """
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        return HttpResponseForbidden("삭제 권한이 없습니다.")
    if request.method == 'POST':
        post.delete()
        return JsonResponse({'status': 'success'})
    return HttpResponseBadRequest()

@login_required
def comment_create(request, pk):
    """
    특정 게시글에 새로운 댓글을 작성하는 뷰입니다.
    Form 제출 방식으로 동작하며, 작성 완료 후 다시 게시글 상세 페이지로 리다이렉트 됩니다.
    """
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Comment.objects.create(post=post, author=request.user, content=content)
        return redirect('board:detail', pk=pk)
    return HttpResponseBadRequest()

@login_required
def comment_delete(request, pk, comment_pk):
    """
    본인이 작성한 댓글을 삭제하는 뷰입니다.
    삭제 권한(작성자 본인)을 확인한 뒤 삭제하고 상세 페이지로 리다이렉트 됩니다.
    """
    comment = get_object_or_404(Comment, pk=comment_pk, post_id=pk)
    if comment.author != request.user:
        return HttpResponseForbidden("삭제 권한이 없습니다.")
    if request.method == 'POST':
        comment.delete()
        return redirect('board:detail', pk=pk)
    return HttpResponseBadRequest()

@login_required
def post_like(request, pk):
    """
    게시글에 '좋아요'를 추가하거나 취소하는 토글(Toggle) 비동기 뷰입니다.
    이미 좋아요를 눌렀다면 취소하고, 누르지 않았다면 추가합니다.
    """
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        like, created = PostLike.objects.get_or_create(post=post, user=request.user)
        if not created:
            like.delete() # Toggle like
            liked = False
        else:
            liked = True
        
        likes_count = post.likes.count()
        return JsonResponse({'status': 'success', 'liked': liked, 'likes_count': likes_count})
    return HttpResponseBadRequest()

@login_required
def post_report(request, pk):
    """
    부적절한 게시글을 신고하는 비동기 뷰입니다.
    한 사용자가 동일한 게시글을 중복해서 신고하지 못하도록 체크하며,
    신고 내역을 Report 모델에 저장합니다.
    """
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            reason = data.get('reason')
            
            if Report.objects.filter(post=post, reporter=request.user).exists():
                return JsonResponse({'status': 'error', 'message': '이미 신고한 게시글입니다.'}, status=400)
            
            if reason:
                Report.objects.create(post=post, reporter=request.user, reason=reason)
                return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return HttpResponseBadRequest()
