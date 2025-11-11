"""
Modelos do Dashboard - Sistema Waze de Alagamentos
================================================

Modelos para representar dados de alagamentos, usuários e interações colaborativas
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid

class Bairro(models.Model):
    """Modelo para bairros - expandido para múltiplas cidades"""
    nome = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100, default='Recife')  # Nova coluna
    uf = models.CharField(max_length=2, default='PE')  # Nova coluna
    zona = models.CharField(max_length=50, blank=True)  # Norte, Sul, Centro, etc.
    latitude = models.FloatField(null=True, blank=True)  # Coordenadas
    longitude = models.FloatField(null=True, blank=True)  # Coordenadas
    populacao = models.IntegerField(null=True, blank=True)
    area_km2 = models.FloatField(null=True, blank=True)
    risco_base = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        help_text="Nível base de risco do bairro (1-4)"
    )
    
    class Meta:
        db_table = 'bairros'
        verbose_name = 'Bairro'
        verbose_name_plural = 'Bairros'
        unique_together = ('nome', 'cidade', 'uf')  # Bairro único por cidade
    
    def __str__(self):
        return self.nome

class UsuarioApp(models.Model):
    """Perfil estendido do usuário para o app"""
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    nome_exibicao = models.CharField(max_length=50, default='Usuário Anônimo')
    pontos_contribuicao = models.IntegerField(default=0)
    nivel_confiabilidade = models.FloatField(default=0.5)  # 0.0 a 1.0
    total_relatos = models.IntegerField(default=0)
    relatos_validados = models.IntegerField(default=0)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'usuarios_app'
        verbose_name = 'Usuário do App'
        verbose_name_plural = 'Usuários do App'
    
    def __str__(self):
        return f"{self.nome_exibicao} ({self.total_relatos} relatos)"
    
    @property
    def taxa_precisao(self):
        """Calcula taxa de precisão do usuário"""
        if self.total_relatos == 0:
            return 0.0
        return self.relatos_validados / self.total_relatos

class RelatorioAlagamento(models.Model):
    """Modelo principal para relatórios de alagamento estilo Waze"""
    
    NIVEL_SEVERIDADE_CHOICES = [
        (1, '🟢 Baixo - Poças d\'água'),
        (2, '🟡 Moderado - Alagamento leve'),
        (3, '🟠 Alto - Alagamento significativo'),
        (4, '🔴 Crítico - Alagamento severo'),
    ]
    
    STATUS_CHOICES = [
        ('ativo', 'Ativo'),
        ('resolvido', 'Resolvido'),
        ('falso_positivo', 'Falso Positivo'),
        ('spam', 'Spam'),
    ]
    
    # Identificação
    id_relato = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    usuario = models.ForeignKey(UsuarioApp, on_delete=models.CASCADE, related_name='relatos')
    
    # Localização
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    bairro = models.ForeignKey(Bairro, on_delete=models.CASCADE)
    endereco_aproximado = models.CharField(max_length=200, blank=True)
    
    # Informações do alagamento
    nivel_severidade = models.IntegerField(
        choices=NIVEL_SEVERIDADE_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(4)]
    )
    descricao = models.TextField(max_length=500, blank=True)
    altura_agua_cm = models.IntegerField(null=True, blank=True, help_text="Altura em centímetros")
    
    # Metadata
    timestamp = models.DateTimeField(default=timezone.now)
    foto = models.ImageField(upload_to='relatos/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ativo')
    
    # Métricas de engajamento
    total_confirmacoes = models.IntegerField(default=0)
    total_negacoes = models.IntegerField(default=0)
    visualizacoes = models.IntegerField(default=0)
    
    # Dados para ML
    confiabilidade_ml = models.FloatField(default=0.5, help_text="Score de confiabilidade do ML")
    validado_automaticamente = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'relatorios_alagamento'
        verbose_name = 'Relatório de Alagamento'
        verbose_name_plural = 'Relatórios de Alagamento'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['bairro', 'nivel_severidade']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Relato {self.get_nivel_severidade_display()} - {self.bairro.nome} - {self.timestamp.strftime('%d/%m %H:%M')}"
    
    @property
    def taxa_confirmacao(self):
        """Taxa de confirmação vs negação"""
        total_interacoes = self.total_confirmacoes + self.total_negacoes
        if total_interacoes == 0:
            return 0.0
        return self.total_confirmacoes / total_interacoes
    
    @property
    def nivel_urgencia(self):
        """Calcula nível de urgência baseado em vários fatores"""
        # Base: severidade
        urgencia = self.nivel_severidade * 25
        
        # Bonus por confirmações
        urgencia += min(self.total_confirmacoes * 5, 20)
        
        # Bonus por confiabilidade do usuário
        urgencia += self.usuario.nivel_confiabilidade * 10
        
        # Penalty por tempo (decresce com o tempo)
        horas_passadas = (timezone.now() - self.timestamp).total_seconds() / 3600
        time_penalty = max(0, 20 - horas_passadas * 2)
        urgencia += time_penalty
        
        return min(100, max(0, urgencia))

class InteracaoRelatorio(models.Model):
    """Interações dos usuários com relatórios (confirmações, negações)"""
    
    TIPO_CHOICES = [
        ('confirmacao', 'Confirmação'),
        ('negacao', 'Negação'),
        ('comentario', 'Comentário'),
        ('atualizacao', 'Atualização de Status'),
    ]
    
    relatorio = models.ForeignKey(RelatorioAlagamento, on_delete=models.CASCADE, related_name='interacoes')
    usuario = models.ForeignKey(UsuarioApp, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    comentario = models.TextField(max_length=300, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    relevante = models.BooleanField(default=True)  # Para filtrar spam
    
    class Meta:
        db_table = 'interacoes_relatorio'
        verbose_name = 'Interação com Relatório'
        verbose_name_plural = 'Interações com Relatórios'
        unique_together = ['relatorio', 'usuario', 'tipo']  # Um usuário só pode confirmar/negar uma vez
        indexes = [
            models.Index(fields=['relatorio', 'tipo']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.usuario.nome_exibicao} - {self.get_tipo_display()} - {self.relatorio.id_relato}"

class AlertaArea(models.Model):
    """Alertas automáticos para áreas com múltiplos alagamentos"""
    
    NIVEL_ALERTA_CHOICES = [
        (1, 'Baixo'),
        (2, 'Moderado'), 
        (3, 'Alto'),
        (4, 'Crítico'),
    ]
    
    bairro = models.ForeignKey(Bairro, on_delete=models.CASCADE)
    nivel_alerta = models.IntegerField(choices=NIVEL_ALERTA_CHOICES)
    total_relatos_ativos = models.IntegerField()
    severidade_media = models.FloatField()
    raio_afetado_metros = models.IntegerField(default=500)
    
    timestamp_criacao = models.DateTimeField(auto_now_add=True)
    timestamp_atualizacao = models.DateTimeField(auto_now=True)
    ativo = models.BooleanField(default=True)
    
    # Dados automáticos
    relatos_origem = models.ManyToManyField(RelatorioAlagamento, related_name='alertas_gerados')
    
    class Meta:
        db_table = 'alertas_area'
        verbose_name = 'Alerta de Área'
        verbose_name_plural = 'Alertas de Área'
        ordering = ['-nivel_alerta', '-timestamp_atualizacao']
    
    def __str__(self):
        return f"Alerta {self.get_nivel_alerta_display()} - {self.bairro.nome} ({self.total_relatos_ativos} relatos)"

class EstatisticaDashboard(models.Model):
    """Cache de estatísticas para performance do dashboard"""
    
    # Dados temporais
    data_referencia = models.DateField()
    hora_referencia = models.IntegerField(null=True, blank=True)  # Para estatísticas horárias
    
    # Métricas agregadas
    total_relatos = models.IntegerField(default=0)
    relatos_criticos = models.IntegerField(default=0)
    relatos_altos = models.IntegerField(default=0)
    relatos_moderados = models.IntegerField(default=0)
    relatos_baixos = models.IntegerField(default=0)
    
    # Engajamento
    total_confirmacoes = models.IntegerField(default=0)
    usuarios_ativos = models.IntegerField(default=0)
    taxa_confirmacao_media = models.FloatField(default=0.0)
    
    # Geográfico
    bairro_mais_afetado = models.CharField(max_length=100, blank=True)
    severidade_media_dia = models.FloatField(default=0.0)
    
    # Metadata
    timestamp_calculo = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'estatisticas_dashboard'
        verbose_name = 'Estatística do Dashboard'
        verbose_name_plural = 'Estatísticas do Dashboard'
        unique_together = ['data_referencia', 'hora_referencia']
        indexes = [
            models.Index(fields=['data_referencia']),
            models.Index(fields=['timestamp_calculo']),
        ]
    
    def __str__(self):
        if self.hora_referencia is not None:
            return f"Stats {self.data_referencia} {self.hora_referencia:02d}h - {self.total_relatos} relatos"
        return f"Stats {self.data_referencia} - {self.total_relatos} relatos"
