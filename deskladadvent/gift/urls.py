from django.urls import path
from gift import views

urlpatterns = [
    path('', views.gift, name='gift'),
    path('roulette/', views.roulette, name='roulette'),
    path('use_promocode/', views.use_promocode, name='use_promocode'),
]
