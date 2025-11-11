"""
Views do Dashboard - Sistema Waze de Alagamentos  
==============================================

Views para dashboard interativo com visualizações e filtros
"""

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Count, Avg, Q, F
from django.utils import timezone
from datetime import datetime, timedelta
import json

from .models import (
    RelatorioAlagamento, Bairro, UsuarioApp, 
    InteracaoRelatorio, AlertaArea
)

def dashboard_home(request):
    """Dashboard principal com métricas e visualizações"""
    
    # Filtros da request
    periodo = request.GET.get('periodo', '7')  # Default 7 dias
    bairro_filtro = request.GET.get('bairro', 'all')
    severidade_filtro = request.GET.get('severidade', 'all')
    
    # Data base para filtros
    data_limite = timezone.now() - timedelta(days=int(periodo))
    
    # Query base
    relatos_query = RelatorioAlagamento.objects.filter(
        timestamp__gte=data_limite,
        status='ativo'
    )
    
    # Aplicar filtros
    if bairro_filtro != 'all':
        relatos_query = relatos_query.filter(bairro__nome=bairro_filtro)
    
    if severidade_filtro != 'all':
        relatos_query = relatos_query.filter(nivel_severidade=int(severidade_filtro))
    
    # MÉTRICAS PRINCIPAIS
    metricas = {
        'total_relatos': relatos_query.count(),
        'relatos_criticos': relatos_query.filter(nivel_severidade=4).count(),
        'relatos_altos': relatos_query.filter(nivel_severidade=3).count(),
        'relatos_moderados': relatos_query.filter(nivel_severidade=2).count(),
        'relatos_baixos': relatos_query.filter(nivel_severidade=1).count(),
        'usuarios_ativos': UsuarioApp.objects.filter(
            relatos__timestamp__gte=data_limite
        ).distinct().count(),
        'total_confirmacoes': sum(r.total_confirmacoes for r in relatos_query),
        'severidade_media': relatos_query.aggregate(
            media=Avg('nivel_severidade')
        )['media'] or 0,
    }
    
    # DADOS PARA GRÁFICOS
    # 1. Relatórios por hora (últimas 24h)
    agora = timezone.now()
    ultima_24h = agora - timedelta(hours=24)
    
    relatos_por_hora = []
    for i in range(24):
        hora_inicio = ultima_24h + timedelta(hours=i)
        hora_fim = hora_inicio + timedelta(hours=1)
        
        count = RelatorioAlagamento.objects.filter(
            timestamp__range=(hora_inicio, hora_fim),
            status='ativo'
        ).count()
        
        relatos_por_hora.append({
            'hora': hora_inicio.strftime('%H:00'),
            'total': count
        })
    
    # 2. Ranking de bairros mais afetados
    bairros_ranking = relatos_query.values(
        'bairro__nome'
    ).annotate(
        total_relatos=Count('id'),
        severidade_media=Avg('nivel_severidade'),
        total_confirmacoes=Count('interacoes')
    ).order_by('-total_relatos')[:10]
    
    # 3. Distribuição de severidade
    severidade_dist = relatos_query.values(
        'nivel_severidade'
    ).annotate(
        total=Count('id')
    ).order_by('nivel_severidade')
    
    # 4. Relatórios recentes para timeline
    relatos_recentes = relatos_query.select_related(
        'bairro', 'usuario'
    ).order_by('-timestamp')[:10]
    
    # 5. Mapa de calor (dados para coordenadas)
    dados_mapa = list(relatos_query.values(
        'latitude', 'longitude', 'nivel_severidade', 
        'bairro__nome', 'timestamp'
    ))
    
    # 6. Tendência temporal (últimos 30 dias)
    ultimos_30_dias = agora - timedelta(days=30)
    
    tendencia_temporal = []
    for i in range(30):
        data_dia = ultimos_30_dias + timedelta(days=i)
        data_inicio = data_dia.replace(hour=0, minute=0, second=0)
        data_fim = data_inicio + timedelta(days=1)
        
        count = RelatorioAlagamento.objects.filter(
            timestamp__range=(data_inicio, data_fim),
            status='ativo'
        ).count()
        
        tendencia_temporal.append({
            'data': data_dia.strftime('%d/%m'),
            'total': count
        })
    
    # ALERTAS ATIVOS
    alertas_ativos = AlertaArea.objects.filter(
        ativo=True
    ).select_related('bairro').order_by('-nivel_alerta')[:5]
    
    # OPÇÕES PARA FILTROS
    opcoes_filtros = {
        'bairros': Bairro.objects.all().order_by('nome'),
        'severidades': [
            {'value': 1, 'label': '🟢 Baixo'},
            {'value': 2, 'label': '🟡 Moderado'},
            {'value': 3, 'label': '🟠 Alto'},
            {'value': 4, 'label': '🔴 Crítico'},
        ]
    }
    
    context = {
        'metricas': metricas,
        'relatos_por_hora': relatos_por_hora,
        'bairros_ranking': bairros_ranking,
        'severidade_distribuicao': severidade_dist,
        'relatos_recentes': relatos_recentes,
        'dados_mapa': dados_mapa,
        'tendencia_temporal': tendencia_temporal,
        'alertas_ativos': alertas_ativos,
        'opcoes_filtros': opcoes_filtros,
        'filtros_aplicados': {
            'periodo': periodo,
            'bairro': bairro_filtro,
            'severidade': severidade_filtro,
        }
    }
    
    return render(request, 'dashboard/home.html', context)

def api_dados_tempo_real(request):
    """API para dados em tempo real (AJAX)"""
    
    # Últimos 10 minutos
    tempo_limite = timezone.now() - timedelta(minutes=10)
    
    novos_relatos = RelatorioAlagamento.objects.filter(
        timestamp__gte=tempo_limite,
        status='ativo'
    ).values(
        'id', 'bairro__nome', 'nivel_severidade', 
        'timestamp', 'latitude', 'longitude'
    )
    
    # Converter para lista e formatar timestamps
    dados = []
    for relato in novos_relatos:
        dados.append({
            'id': relato['id'],
            'bairro': relato['bairro__nome'],
            'severidade': relato['nivel_severidade'],
            'timestamp': relato['timestamp'].strftime('%H:%M'),
            'latitude': float(relato['latitude']),
            'longitude': float(relato['longitude']),
        })
    
    return JsonResponse({
        'novos_relatos': dados,
        'total_novos': len(dados),
        'timestamp_atualizacao': timezone.now().strftime('%H:%M:%S')
    })

def relatorio_detalhado(request, relato_id):
    """Página de detalhes de um relatório específico"""
    
    relatorio = get_object_or_404(
        RelatorioAlagamento.objects.select_related(
            'bairro', 'usuario'
        ),
        id=relato_id
    )
    
    # Incrementar visualizações
    relatorio.visualizacoes = F('visualizacoes') + 1
    relatorio.save(update_fields=['visualizacoes'])
    
    # Buscar interações
    interacoes = InteracaoRelatorio.objects.filter(
        relatorio=relatorio,
        relevante=True
    ).select_related('usuario').order_by('-timestamp')[:20]
    
    # Relatórios próximos (mesmo bairro, últimas 24h)
    relatos_proximos = RelatorioAlagamento.objects.filter(
        bairro=relatorio.bairro,
        timestamp__gte=timezone.now() - timedelta(hours=24),
        status='ativo'
    ).exclude(id=relatorio.id).order_by('-timestamp')[:5]
    
    context = {
        'relatorio': relatorio,
        'interacoes': interacoes,
        'relatos_proximos': relatos_proximos,
        'pode_interagir': True,  # Implementar lógica de permissões
    }
    
    return render(request, 'dashboard/relatorio_detalhes.html', context)

def mapa_interativo(request):
    """Página do mapa interativo"""
    
    # Filtros
    severidade_min = request.GET.get('sev_min', '1')
    periodo_horas = request.GET.get('periodo', '24')
    
    # Filtrar relatórios
    tempo_limite = timezone.now() - timedelta(hours=int(periodo_horas))
    
    relatos = RelatorioAlagamento.objects.filter(
        timestamp__gte=tempo_limite,
        nivel_severidade__gte=int(severidade_min),
        status='ativo'
    ).select_related('bairro')
    
    # Preparar dados para o mapa
    dados_mapa = []
    for relato in relatos:
        dados_mapa.append({
            'id': relato.id,
            'lat': float(relato.latitude),
            'lng': float(relato.longitude),
            'severidade': relato.nivel_severidade,
            'bairro': relato.bairro.nome,
            'timestamp': relato.timestamp.strftime('%d/%m %H:%M'),
            'confirmacoes': relato.total_confirmacoes,
            'descricao': relato.descricao or 'Sem descrição',
        })
    
    # Estatísticas por bairro para heatmap
    stats_bairros = relatos.values(
        'bairro__nome'
    ).annotate(
        total=Count('id'),
        severidade_media=Avg('nivel_severidade')
    ).order_by('-total')
    
    context = {
        'dados_mapa': json.dumps(dados_mapa),
        'stats_bairros': stats_bairros,
        'filtros': {
            'severidade_min': severidade_min,
            'periodo_horas': periodo_horas,
        },
        'total_relatos': len(dados_mapa),
    }
    
    return render(request, 'dashboard/mapa.html', context)

def analytics(request):
    """Página de analytics avançados"""
    
    # Análise temporal detalhada
    ultimos_90_dias = timezone.now() - timedelta(days=90)
    
    # Tendências por mês
    tendencias_mensais = RelatorioAlagamento.objects.filter(
        timestamp__gte=ultimos_90_dias
    ).extra(
        select={'mes': 'EXTRACT(month FROM timestamp)'}
    ).values('mes').annotate(
        total=Count('id'),
        severidade_media=Avg('nivel_severidade')
    ).order_by('mes')
    
    # Padrões por hora do dia
    padroes_horarios = RelatorioAlagamento.objects.filter(
        timestamp__gte=ultimos_90_dias
    ).extra(
        select={'hora': 'EXTRACT(hour FROM timestamp)'}
    ).values('hora').annotate(
        total=Count('id')
    ).order_by('hora')
    
    # Top usuários contribuidores
    top_usuarios = UsuarioApp.objects.annotate(
        relatos_periodo=Count(
            'relatos',
            filter=Q(relatos__timestamp__gte=ultimos_90_dias)
        )
    ).filter(relatos_periodo__gt=0).order_by('-relatos_periodo')[:10]
    
    # Correlação severidade vs confirmações
    correlacao_dados = list(RelatorioAlagamento.objects.filter(
        timestamp__gte=ultimos_90_dias
    ).values('nivel_severidade', 'total_confirmacoes'))
    
    context = {
        'tendencias_mensais': tendencias_mensais,
        'padroes_horarios': padroes_horarios,
        'top_usuarios': top_usuarios,
        'correlacao_dados': json.dumps(correlacao_dados),
        'periodo_analise': 90,
    }
    
    return render(request, 'dashboard/analytics.html', context)
