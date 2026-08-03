from django.urls import path
from . import views

app_name = "account"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("logout/", views.logout_view, name="logout"),
    path('update/', views.profile_update_view, name='update'),
    path('delete/', views.delete_account_view, name='delete'),
    path('posts/', views.my_posts_view, name='my_posts'),
]