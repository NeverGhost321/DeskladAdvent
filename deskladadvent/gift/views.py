from django.conf import settings
from django.shortcuts import render
from .models import Gifts, PromoCode_gift
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from userpromocode.models import Promocode_user

def gift(request):
    
    return render(request, 'gift/gift.html')

def roulette(request):
    from_cards = request.GET.get('from_cards', None)

    # Сохраняем состояние кнопки в сессии
    if from_cards:
        request.session['button_active'] = True
    else:
        request.session['button_active'] = False

    button_active = request.session.get('button_active', False)  # по умолчанию False, если нет состояния

    # Пример данных подарков (для использования в вашем шаблоне)
    gifts = Gifts.objects.all().values('id', 'name', 'chance', 'gift_img', 'is_avaible', 'number_of_gifts')

    for gift in gifts:
        promocodes = PromoCode_gift.objects.filter(gift_id=gift['id']).values('code', 'is_used')
        gift['promocodes'] = list(promocodes)

        available_promocodes = [promo for promo in promocodes if not promo['is_used']]

        if available_promocodes:
            gift['chance'] = gift['chance']
        else:
            gift['chance'] = 0

    gifts_list = list(gifts)
    available_gifts_count = sum(len([promo for promo in gift['promocodes'] if not promo['is_used']]) for gift in gifts_list)

    return render(request, 'gift/roulette.html', {
        'gifts': json.dumps(gifts_list),
        'button_active': button_active,
        'available_gifts_count': available_gifts_count  # Количество доступных подарков
    })

@csrf_exempt
def use_promocode(request):
    if request.method == 'POST':
        promo_code = request.POST.get('promo_code')
        try:
            promocode = PromoCode_gift.objects.get(code=promo_code)
            
            # Проверка, использован ли промокод
            if promocode.is_used:
                return JsonResponse({'status': 'error', 'message': 'Промокод уже использован'})
            
            # Проверка, авторизован ли пользователь
            if not request.user.is_authenticated:
                return JsonResponse({'status': 'error', 'message': 'Пользователь не авторизован'})
            
            # Получаем или создаем привязку пользователя с промокодом
            promocode_user, created = Promocode_user.objects.get_or_create(user=request.user)

            # Проверяем, есть ли у пользователя уже 7 привязанных промокодов
            if promocode_user.promocodes.count() >= 7:
                return JsonResponse({'status': 'error', 'message': 'У пользователя уже есть 7 привязанных промокодов'})

            # Добавляем промокод к пользователю
            promocode_user.promocodes.add(promocode)

            # Маркируем промокод как использованный
            promocode.is_used = True
            promocode.save()

            return JsonResponse({'status': 'success', 'message': 'Промокод успешно использован и привязан к пользователю'})

        except PromoCode_gift.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Промокод не найден'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Неверный запрос'})