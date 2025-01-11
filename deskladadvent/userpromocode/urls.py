# Пример urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('userpromocode/', views.promocode_login, name='promocode_login'),
    path('gift/', views.gift, name='gift'),  # Страница подарков
]
