from django.conf import settings
from django.db import models

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rank = models.CharField(max_length=20) # 계급
    enlist_date = models.DateField() # 입대일
    discharge_date = models.DateField() # 전역(예정)일
