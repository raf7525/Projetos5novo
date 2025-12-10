"""
URLs do Dashboard
"""
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('teste/', views.teste_dados, name='teste'),
    path('mapa/', views.mapa_interativo, name='mapa'),
    path('analytics/', views.analytics, name='analytics'),
    path('relatorio/<int:relato_id>/', views.relatorio_detalhado, name='relatorio_detalhes'),
    path('api/tempo-real/', views.api_dados_tempo_real, name='api_tempo_real'),
    path('relatar/', views.criar_relatorio, name='criar_relatorio'),
]