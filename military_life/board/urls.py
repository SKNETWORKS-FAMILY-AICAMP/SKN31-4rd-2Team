from django.urls import path
from . import views

app_name = "board"

urlpatterns = [
    # 게시판 메인 피드 (목록) 조회
    path("", views.post_list, name="list"),
    
    # 새 게시글 작성 (Ajax 처리)
    path("create/", views.post_create, name="create"),
    
    # 특정 게시글 상세 조회
    path("<int:pk>/", views.post_detail, name="detail"),
    
    # 특정 게시글 수정 (본인만, Ajax 처리)
    path("<int:pk>/update/", views.post_update, name="update"),
    
    # 특정 게시글 삭제 (본인만, Ajax 처리)
    path("<int:pk>/delete/", views.post_delete, name="delete"),
    
    # 좋아요 버튼 토글 (Ajax 처리)
    path("<int:pk>/like/", views.post_like, name="like"),
    
    # 게시글 신고 (Ajax 처리)
    path("<int:pk>/report/", views.post_report, name="report"),
    
    # 특정 게시글에 댓글 작성
    path("<int:pk>/comments/create/", views.comment_create, name="comment_create"),
    
    # 특정 댓글 삭제 (본인만)
    path("<int:pk>/comments/<int:comment_pk>/delete/", views.comment_delete, name="comment_delete"),
]