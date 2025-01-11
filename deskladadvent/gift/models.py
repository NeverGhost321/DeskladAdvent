from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone

import random
import string
from django.db import models
# Create your models here.
# Модель подарков
# Модель подарков
# Модель подарков
class Gifts(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True, verbose_name="Название подарка")
    number_of_gifts = models.PositiveIntegerField(default=0, verbose_name="Количество подарка")
    gift_img = models.ImageField(upload_to='gifts/', null=True, blank=True, verbose_name="Партинка подарка")
    is_avaible = models.BooleanField(default=True)
    chance = models.PositiveIntegerField(default=0, verbose_name="Шанс (%)", help_text="Шанс")
    available_date = models.DateField(null=True, blank=True, verbose_name="Дата доступности", help_text="Дата когда подарок будет доступен")

    def __str__(self):
        return self.name

    # Метод для генерации случайных промокодов
    def generate_promocodes(self):
        promocodes = []
        for _ in range(self.number_of_gifts):
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=9))  # Генерация случайного промокода
            promocodes.append(code)
        return promocodes

    def save(self, *args, **kwargs):
        # Получаем все текущие промокоды для подарка
        current_promocodes = PromoCode_gift.objects.filter(gift=self)
        current_promocodes_count = current_promocodes.count()

        # Если количество подарков уменьшилось, удаляем лишние промокоды
        if current_promocodes_count > self.number_of_gifts:
            # Рассчитываем, сколько промокодов нужно удалить
            promocodes_to_delete_count = current_promocodes_count - self.number_of_gifts
            promocodes_to_delete = current_promocodes[:promocodes_to_delete_count]  # Берем первые `promocodes_to_delete_count` промокодов
            for promocode in promocodes_to_delete:
                promocode.delete()

        # Если количество подарков увеличилось, добавляем недостающие промокоды
        if current_promocodes_count < self.number_of_gifts:
            promocodes_to_add_count = self.number_of_gifts - current_promocodes_count
            promocodes = self.generate_promocodes()
            for code in promocodes[:promocodes_to_add_count]:
                PromoCode_gift.objects.create(gift=self, code=code)

        super().save(*args, **kwargs)  # Вызов сохранения родительского класса



# Модель промокодов
class PromoCode_gift(models.Model):
    gift = models.ForeignKey(Gifts, related_name='promocodes', on_delete=models.CASCADE, verbose_name="Подарок")
    code = models.CharField(max_length=50, unique=True, verbose_name="Промокод")
    is_used = models.BooleanField(default=False, verbose_name="Использован ли промокод")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return f"Промокод для {self.gift.name}: {self.code}"

class GiftCard(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True, verbose_name="Название подарка")
    gift_img = models.ImageField(upload_to='cards/', null=True, blank=True, verbose_name="Партинка подарка")
    is_available = models.BooleanField(default=False, verbose_name="Доступна ли карточка")
    sequence_number = models.PositiveIntegerField(default=0, verbose_name="Порядковый номер карточки")
    

    def available_date_for_user(self, user):
        if user.date_joined:
            return user.date_joined + timedelta(days=(self.sequence_number - 1))  # Убираем умножение на 24
        return None

    def is_card_available(self, user):
        available_date = self.available_date_for_user(user)
        return available_date and available_date <= timezone.now()

    def __str__(self):
        return self.name