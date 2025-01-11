from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import JsonResponse
from .models import Promocode_user
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from gift.models import GiftCard
from django.utils import timezone
from datetime import timedelta
# Главная страница
def index(request):
    # Считаем только промокоды, у которых есть пользователь
    total_promocodes = Promocode_user.objects.filter(user__isnull=True).count()  
    max_promocodes = 300  # Задаем максимальное значение

    return render(request, 'userpromocode/index.html', {
        'total_promocodes': total_promocodes,
        'max_promocodes': max_promocodes,
    })
    
@login_required
def gift(request):
    # Получаем пользователя
    promocodes_user = Promocode_user.objects.get(user=request.user)
    user_creation_date = promocodes_user.user_creation_date
    promocodes = promocodes_user.promocodes.all()

    # Получаем все карточки
    cards = GiftCard.objects.order_by('sequence_number')  # Сортируем карточки по порядковому номеру

    # Список данных карточек
    cards_data = []
    available_cards_count = 0  # Количество доступных карточек

    for i, card in enumerate(cards[:7]):  # Берем только первые 7 карточек
        # Кумулятивное количество часов (первая карточка доступна сразу, вторая через 24 часа и т.д.)
        cumulative_hours = i * 24  # Для первой карточки будет 0, для второй 24, для третьей 48 и т.д.

        # Рассчитываем дату доступности для каждой карточки
        available_date = user_creation_date + timedelta(hours=cumulative_hours)

        is_available = timezone.now() >= available_date

        # Рассчитываем оставшееся время
        if is_available:
            remaining_hours = 0
            remaining_minutes = 0
            remaining_seconds = 0
        else:
            remaining_time = available_date - timezone.now()
            remaining_seconds_total = int(remaining_time.total_seconds())
            remaining_hours = max(0, remaining_seconds_total // 3600)
            remaining_minutes = max(0, (remaining_seconds_total % 3600) // 60)
            remaining_seconds = max(0, remaining_seconds_total % 60)  # Секунды
        
        cards_data.append({
            'card': card,
            'available_date': available_date,
            'is_available': is_available,
            'remaining_hours': remaining_hours,
            'remaining_minutes': remaining_minutes,
            'remaining_seconds': remaining_seconds,  # Добавить оставшиеся секунды
        })
        
    return render(request, 'gift/gift.html', {
        'promocodes': promocodes,
        'user_name': request.user.username,
        'cards_data': cards_data,
        'available_cards_count': available_cards_count,  # Количество доступных карточек
    })

def promocode_login(request):
    if request.method == 'POST':
        promocode = request.POST.get('input_form', '').strip().replace('-', '')
        try:
            promo = Promocode_user.objects.get(code=promocode)

            # Если промокод найден, проверяем, привязан ли пользователь
            if promo.user is None:
                user_count = User.objects.filter(username__startswith='user').count()
                username = f'user_{user_count + 1}'
                user = User.objects.create_user(username=username, password=promocode)
                promo.user = user
                promo.save()

            # Авторизация
            user = authenticate(request, username=promo.user.username, password=promocode)
            if user:
                login(request, user)

                # Обновляем дату создания пользователя, если она еще не установлена
                if promo.user_creation_date is None:
                    promo.user_creation_date = timezone.now()
                    promo.save()

                # Получаем все привязанные промокоды для подарков
                promocodes = promo.promocodes.all()

                # Формируем список привязанных промокодов для подарков
                promocodes_list = [{'id': p.id, 'code': p.code} for p in promocodes]

                # Формируем ответ с промокодом пользователя и привязанными промокодами подарков
                return JsonResponse({
                    'success': True, 
                    'redirect_url': '/gift/', 
                    'user': {'username': promo.user.username, 'user_id': promo.user.id},
                    'promocode': promo.code,
                    'promocodes': promocodes_list
                })
            else:
                return JsonResponse({'success': False, 'message': 'Ошибка авторизации!'})

        except Promocode_user.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Неверный промокод!'})

    # На случай неправильного запроса
    return JsonResponse({'success': False, 'message': 'Некорректный запрос.'})