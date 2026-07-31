from django.conf import settings
from django.db import models

class Profile(models.Model):
    class Status(models.TextChoices):
        ENLISTED = "병사", "병사"
        OFFICER = "간부", "간부"
 
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ENLISTED) # 신분(병사/간부) - 회원가입 화면 반영
    rank = models.CharField(max_length=20) # 계급
    enlist_date = models.DateField() # 입대일
    discharge_date = models.DateField() # 전역(예정)일
 
    def __str__(self):
        return f"{self.user} ({self.status}/{self.rank})"