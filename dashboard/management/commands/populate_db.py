"""
Comando Django para popular banco de dados
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from dashboard.models import Bairro, UsuarioApp, RelatorioAlagamento, InteracaoRelatorio
from django.utils import timezone
from django.db.models import Count, Avg, Sum
import pandas as pd
from datetime import datetime

class Command(BaseCommand):
    help = 'Popula banco de dados com dados do CSV'

    def handle(self, *args, **options):
        self.stdout.write("🌊 POPULANDO BANCO DE DADOS")
        
        # Popular bairros
        self.popular_bairros()
        
        # Criar usuários
        usuarios_map = self.criar_usuarios()
        
        # Migrar relatórios
        self.migrar_relatorios(usuarios_map)
        
        self.stdout.write(
            self.style.SUCCESS('✅ Banco populado com sucesso!')
        )
    
    def popular_bairros(self):
        """Popula bairros"""
        bairros_data = [
            ('Espinheiro', 'Norte', 2),
            ('Gracas', 'Norte', 2), 
            ('Santo Amaro', 'Norte', 3),
            ('Boa Viagem', 'Sul', 4),
            ('Varzea', 'Oeste', 2),
            ('Afogados', 'Oeste', 3),
            ('Imbiribeira', 'Sul', 4),
            ('Madalena', 'Norte', 2),
            ('Recife Antigo', 'Centro', 2),
            ('Cidade Universitaria', 'Oeste', 1),
        ]
        
        for nome, zona, risco in bairros_data:
            _, created = Bairro.objects.get_or_create(
                nome=nome,
                defaults={'zona': zona, 'risco_base': risco}
            )
            if created:
                self.stdout.write(f"✅ Bairro criado: {nome}")
    
    def criar_usuarios(self):
        """Cria usuários"""
        df = pd.read_csv('data/raw/data.csv')
        user_ids = df['id_usuario'].unique()
        usuarios_map = {}
        
        for i, user_id in enumerate(user_ids):
            username = f"user_{user_id.split('_')[1]}"
            
            django_user, _ = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f"{username}@flood.app",
                    'first_name': f"Usuário {i+1}"
                }
            )
            
            usuario_app, created = UsuarioApp.objects.get_or_create(
                usuario=django_user,
                defaults={
                    'nome_exibicao': f"Colaborador {i+1}",
                    'nivel_confiabilidade': 0.7,
                }
            )
            
            usuarios_map[user_id] = usuario_app
            
            if created:
                self.stdout.write(f"✅ Usuário criado: {usuario_app.nome_exibicao}")
        
        return usuarios_map
    
    def migrar_relatorios(self, usuarios_map):
        """Migra relatórios do CSV"""
        df = pd.read_csv('data/raw/data.csv')
        
        for _, row in df.iterrows():
            try:
                bairro = Bairro.objects.get(nome=row['bairro'])
                usuario = usuarios_map[row['id_usuario']]
                
                timestamp = pd.to_datetime(row['timestamp'])
                
                RelatorioAlagamento.objects.create(
                    usuario=usuario,
                    latitude=row['latitude'],
                    longitude=row['longitude'],
                    bairro=bairro,
                    nivel_severidade=row['nivel_severidade'],
                    timestamp=timezone.make_aware(timestamp) if timezone.is_naive(timestamp) else timestamp,
                    total_confirmacoes=row['confirmacoes'],
                    endereco_aproximado=f"Região do {bairro.nome}",
                    descricao=f"Alagamento nível {row['nivel_severidade']}",
                )
                
                self.stdout.write(f"📍 Relato: {bairro.nome} - Nível {row['nivel_severidade']}")
                
            except Exception as e:
                self.stdout.write(f"❌ Erro: {e}")