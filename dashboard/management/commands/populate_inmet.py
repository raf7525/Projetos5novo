"""
Comando Django para popular banco com dados INMET
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from dashboard.models import Bairro, UsuarioApp, RelatorioAlagamento, InteracaoRelatorio
from django.utils import timezone
from django.db.models import Count, Avg, Sum
import pandas as pd
from datetime import datetime
import pytz
import os

class Command(BaseCommand):
    help = 'Popula banco de dados com dados baseados no INMET'

    def handle(self, *args, **options):
        self.stdout.write("🌧️ POPULANDO COM DADOS INMET")
        
        # Arquivo com dados sintéticos baseados no INMET
        csv_path = "/home/raf75/quinto-periodo/projetos/Projetos5novo/data/raw/alagamentos_inmet_synthetic.csv"
        
        if not os.path.exists(csv_path):
            self.stdout.write(
                self.style.ERROR(f'❌ Arquivo não encontrado: {csv_path}')
            )
            return
        
        # Limpar dados existentes
        self.stdout.write("🗑️ Limpando dados antigos...")
        RelatorioAlagamento.objects.all().delete()
        InteracaoRelatorio.objects.all().delete()
        UsuarioApp.objects.all().delete()
        # Limpar usuários Django também (exceto superuser)
        User.objects.filter(is_superuser=False).delete()
        Bairro.objects.all().delete()
        
        # Carregar dados
        df = pd.read_csv(csv_path)
        self.stdout.write(f"📊 Carregando {len(df)} registros do INMET...")
        
        # Criar bairros únicos
        bairros_cidades = df.groupby(['bairro', 'cidade', 'uf']).size().reset_index(name='count')
        
        self.stdout.write("🏘️ Criando bairros...")
        for _, row in bairros_cidades.iterrows():
            bairro = Bairro.objects.create(
                nome=row['bairro'],
                cidade=row['cidade'],
                uf=row['uf'],
                latitude=df[df['bairro'] == row['bairro']]['latitude'].iloc[0],
                longitude=df[df['bairro'] == row['bairro']]['longitude'].iloc[0],
            )
            self.stdout.write(f"   ✅ {bairro.nome}, {bairro.cidade}/{bairro.uf}")
        
        # Criar usuários únicos
        usuarios_unicos = df['usuario'].unique()
        usuarios_map = {}
        
        self.stdout.write("👥 Criando usuários...")
        for i, usuario_id in enumerate(usuarios_unicos[:20]):  # Limite de 20 usuários
            # Criar User do Django
            user = User.objects.create_user(
                username=usuario_id,
                email=f'{usuario_id}@waze-alagamentos.com',
                password='senha123'
            )
            
            # Criar perfil de usuário
            usuario_app = UsuarioApp.objects.create(
                usuario=user,
                nome_exibicao=f'Usuário {usuario_id}',
                nivel_confiabilidade=0.3 + (i % 7) * 0.1,  # Varia entre 0.3-0.9
                total_relatos=0,
                relatos_validados=0
            )
            
            usuarios_map[usuario_id] = usuario_app
            self.stdout.write(f"   ✅ {usuario_id} (confiabilidade: {usuario_app.nivel_confiabilidade})")
        
        # Migrar relatórios de alagamento
        self.stdout.write("💧 Migrando relatórios de alagamento...")
        
        relatorios_criados = 0
        
        for _, row in df.iterrows():
            try:
                # Encontrar bairro
                bairro = Bairro.objects.get(
                    nome=row['bairro'], 
                    cidade=row['cidade'],
                    uf=row['uf']
                )
                
                # Usuário (usar mapeamento ou criar genérico)
                usuario_app = usuarios_map.get(row['usuario'])
                if not usuario_app:
                    # Usar primeiro usuário como fallback
                    usuario_app = list(usuarios_map.values())[0]
                
                # Converter data para timezone aware
                brasil_tz = pytz.timezone('America/Sao_Paulo')
                data_ocorrencia = pd.to_datetime(row['data'])
                if data_ocorrencia.tz is None:
                    data_ocorrencia = brasil_tz.localize(data_ocorrencia)
                
                # Criar relatório
                relatorio = RelatorioAlagamento.objects.create(
                    usuario=usuario_app,
                    timestamp=data_ocorrencia,
                    bairro=bairro,
                    latitude=float(row['latitude']),
                    longitude=float(row['longitude']),
                    nivel_severidade=int(row['severidade']),
                    descricao=row['descricao'],
                    total_confirmacoes=int(row['confirmacoes']),
                    status='ativo'
                )
                
                # Criar interações (confirmações) - cada usuário confirma no máximo uma vez
                num_confirmacoes = min(int(row['confirmacoes']), len(usuarios_map) - 1)  # -1 para excluir o autor
                outros_usuarios = [u for u in usuarios_map.values() if u != usuario_app]
                
                if outros_usuarios:
                    import random
                    # Selecionar usuários únicos para confirmações
                    confirmadores = random.sample(outros_usuarios, min(num_confirmacoes, len(outros_usuarios)))
                    
                    for confirmador in confirmadores:
                        InteracaoRelatorio.objects.create(
                            relatorio=relatorio,
                            usuario=confirmador,
                            tipo='confirmacao'
                        )
                
                relatorios_criados += 1
                
                if relatorios_criados % 20 == 0:
                    self.stdout.write(f"   📊 {relatorios_criados} relatórios processados...")
                    
            except Exception as e:
                self.stdout.write(f"   ❌ Erro ao processar linha: {e}")
                continue
        
        # Atualizar contadores de usuários
        self.stdout.write("🔄 Atualizando estatísticas de usuários...")
        for usuario_app in UsuarioApp.objects.all():
            usuario_app.total_relatos = RelatorioAlagamento.objects.filter(usuario=usuario_app).count()
            usuario_app.relatos_validados = RelatorioAlagamento.objects.filter(
                usuario=usuario_app, 
                status='ativo'
            ).count()
            usuario_app.save()
        
        # Estatísticas finais
        total_relatorios = RelatorioAlagamento.objects.count()
        total_bairros = Bairro.objects.count()
        total_usuarios = UsuarioApp.objects.count()
        total_interacoes = InteracaoRelatorio.objects.count()
        
        self.stdout.write("\n📈 ESTATÍSTICAS FINAIS:")
        self.stdout.write(f"   📍 Bairros criados: {total_bairros}")
        self.stdout.write(f"   👥 Usuários criados: {total_usuarios}")
        self.stdout.write(f"   💧 Relatórios de alagamento: {total_relatorios}")
        self.stdout.write(f"   🤝 Interações (confirmações): {total_interacoes}")
        
        # Dados por severidade
        severidades = RelatorioAlagamento.objects.values('nivel_severidade').annotate(
            total=Count('id')
        ).order_by('nivel_severidade')
        
        self.stdout.write("\n⚠️ DISTRIBUIÇÃO POR SEVERIDADE:")
        labels = {1: 'Baixo', 2: 'Moderado', 3: 'Alto', 4: 'Crítico'}
        for sev in severidades:
            label = labels[sev['nivel_severidade']]
            self.stdout.write(f"   {label}: {sev['total']} casos")
        
        # Top 5 cidades
        cidades = Bairro.objects.values('cidade').annotate(
            total_relatorios=Count('relatorioalagamento')
        ).order_by('-total_relatorios')[:5]
        
        self.stdout.write("\n🏙️ TOP 5 CIDADES:")
        for cidade in cidades:
            self.stdout.write(f"   {cidade['cidade']}: {cidade['total_relatorios']} relatórios")
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✅ Banco populado com dados INMET! {total_relatorios} relatórios carregados.')
        )