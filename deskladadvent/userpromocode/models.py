from django.db import models
from django.core.exceptions import ValidationError
import re
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User

from django.utils import timezone

class Promocode_user(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Пользователь", null=True, blank=True)
    code = models.CharField(max_length=9, unique=True, verbose_name="Промокод")
    count_gifts = models.PositiveIntegerField(default=7)
    user_creation_date = models.DateTimeField(null=True, blank=True, verbose_name="Дата создания пользователя")  # Убрали default
    promocodes = models.ManyToManyField('gift.PromoCode_gift', blank=True, related_name='users', verbose_name="Привязанные промокоды")
    
    class Meta:
        verbose_name = "Промокод пользователя"
        verbose_name_plural = "Промокоды пользователей"

    def __str__(self):
        return f"{self.code} ({self.user.username if self.user else 'Не привязан'})"
    
