from django.urls import path
from . import views

app_name = "chatbot"

urlpatterns = [
    path("", views.chat, name="chat"),
    path("api/message/", views.send_message, name="send_message"),
]