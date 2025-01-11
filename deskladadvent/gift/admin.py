from django.contrib import admin
from .models import Gifts, PromoCode_gift, GiftCard

# Встроенный класс для отображения промокодов в админке
class PromoCode_giftInline(admin.TabularInline):
    model = PromoCode_gift
    extra = 0  # Количество пустых строк для добавления (не будет лишних пустых строк)

# Класс для админки модели Gifts
class GiftsAdmin(admin.ModelAdmin):
    list_display = ('name', 'number_of_gifts', 'is_avaible', 'available_date')
    inlines = [PromoCode_giftInline]  # Встраиваем промокоды в админку
    search_fields = ('name',)  # Добавляем поиск по имени подарка

# Регистрируем модели с настройками админки
admin.site.register(Gifts, GiftsAdmin)
admin.site.register(PromoCode_gift)
admin.site.register(GiftCard)
