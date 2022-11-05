from django.db import models

from core.models import User


class TgUser(models.Model):
    chat_id = models.BigIntegerField(verbose_name='Chat ID', unique=True)
    user_ud = models.CharField(verbose_name='User UD', max_length=255, null=True, blank=True, default=None)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, default=None)
    verification_code = models.CharField(max_length=32, null=True, blank=True, default=None)

