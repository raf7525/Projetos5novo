"""
Script para Popular o Banco de Dados com Dados do CSV
=====================================================

Migra os dados do CSV para o banco Django para uso no dashboard
"""

import os
import sys
import django
from datetime import datetime
import pandas as pd

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth.models import User
from dashboard.models import Bairro, UsuarioApp, RelatorioAlagamento, InteracaoRelatorio
from django.utils import timezone
import uuid

def popular_bairros():
    """Popula tabela de bairros"""
    bairros_recife = [
        ('Espinheiro', 'Norte', 30000, 2.5, 2),
        ('Gracas', 'Norte', 90000, 8.1, 2),
        ('Santo Amaro', 'Norte', 15000, 1.2, 3),
        ('Boa Viagem', 'Sul', 120000, 7.5, 4),  # Área costeira
        ('Varzea', 'Oeste', 80000, 15.3, 2),
        ('Afogados', 'Oeste', 45000, 3.2, 3),
        ('Imbiribeira', 'Sul', 40000, 3.8, 4),  # Próximo ao rio
        ('Madalena', 'Norte', 25000, 2.1, 2),
        ('Recife Antigo', 'Centro', 5000, 0.8, 2),
        ('Cidade Universitaria', 'Oeste', 35000, 4.5, 1),
    ]
    
    print("📍 Populando bairros...")
    for nome, zona, pop, area, risco in bairros_recife:
        bairro, created = Bairro.objects.get_or_create(
            nome=nome,
            defaults={
                'zona': zona,
                'populacao': pop,
                'area_km2': area,
                'risco_base': risco
            }
        )
        if created:
            print(f"   ✅ Criado: {nome}")
        else:
            print(f"   📍 Existe: {nome}")

def criar_usuarios_anonimos():
    """Cria usuários baseados nos IDs do CSV"""
    print("\n👥 Criando usuários...")
    
    # Ler CSV para pegar IDs únicos de usuários
    df = pd.read_csv('data/raw/data.csv')
    user_ids = df['id_usuario'].unique()
    
    usuarios_criados = []
    
    for i, user_id in enumerate(user_ids):
        # Criar usuário Django se não existir
        username = f"user_{user_id.split('_')[1]}"
        django_user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': f"{username}@flood.app",
                'first_name': f"Usuário {i+1}"
            }
        )
        
        # Calcular estatísticas do usuário baseado no CSV
        user_data = df[df['id_usuario'] == user_id]
        total_relatos = len(user_data)
        confirmacoes_media = user_data['confirmacoes'].mean()
        
        # Criar perfil de usuário do app
        usuario_app, created = UsuarioApp.objects.get_or_create(
            usuario=django_user,
            defaults={
                'nome_exibicao': f"Colaborador {i+1}",
                'total_relatos': total_relatos,
                'relatos_validados': int(total_relatos * 0.8),  # 80% validados
                'pontos_contribuicao': int(confirmacoes_media * total_relatos * 10),
                'nivel_confiabilidade': min(0.9, 0.3 + (confirmacoes_media / 20))  # Baseado em confirmações
            }
        )
        
        usuarios_criados.append((user_id, usuario_app))
        
        if created:
            print(f"   ✅ Criado: {usuario_app.nome_exibicao} ({total_relatos} relatos)")
        else:
            print(f"   👥 Existe: {usuario_app.nome_exibicao}")
    
    return dict(usuarios_criados)

def migrar_relatorios_csv():
    """Migra dados do CSV para o banco Django"""
    print("\n📊 Migrando relatórios do CSV...")
    
    # Carregar dados
    df = pd.read_csv('data/raw/data.csv')
    usuarios_map = criar_usuarios_anonimos()
    
    relatorios_criados = 0
    
    for _, row in df.iterrows():
        try:
            # Buscar bairro e usuário
            bairro = Bairro.objects.get(nome=row['bairro'])
            usuario = usuarios_map[row['id_usuario']]
            
            # Converter timestamp
            timestamp = pd.to_datetime(row['timestamp'])
            
            # Criar relatório
            relatorio = RelatorioAlagamento.objects.create(
                usuario=usuario,
                latitude=row['latitude'],
                longitude=row['longitude'],
                bairro=bairro,
                nivel_severidade=row['nivel_severidade'],
                timestamp=timezone.make_aware(timestamp) if timezone.is_naive(timestamp) else timestamp,
                total_confirmacoes=row['confirmacoes'],
                endereco_aproximado=f"Próximo ao {bairro.nome}",
                descricao=f"Alagamento reportado por {usuario.nome_exibicao}",
                confiabilidade_ml=0.7 + (row['confirmacoes'] / 20) * 0.3  # Score baseado em confirmações
            )
            
            # Criar algumas interações simuladas
            if row['confirmacoes'] > 0:
                criar_interacoes_simuladas(relatorio, row['confirmacoes'])
            
            relatorios_criados += 1
            print(f"   📍 Relato {relatorios_criados}: {bairro.nome} - Nível {row['nivel_severidade']}")
            
        except Exception as e:
            print(f"   ❌ Erro ao processar linha {row['id_relato']}: {e}")
    
    print(f"\n✅ Total de relatórios migrados: {relatorios_criados}")

def criar_interacoes_simuladas(relatorio, total_confirmacoes):
    """Cria interações simuladas para dar realismo"""
    # Pegar alguns usuários aleatórios para interagir
    usuarios = UsuarioApp.objects.exclude(id=relatorio.usuario.id)[:min(total_confirmacoes, 5)]
    
    for i, usuario in enumerate(usuarios):
        if i < total_confirmacoes * 0.8:  # 80% confirmações
            InteracaoRelatorio.objects.create(
                relatorio=relatorio,
                usuario=usuario,
                tipo='confirmacao',
                comentario=f"Confirmado por {usuario.nome_exibicao}"
            )
        else:  # 20% comentários
            InteracaoRelatorio.objects.create(
                relatorio=relatorio,
                usuario=usuario,
                tipo='comentario',
                comentario=f"Situação vista em {relatorio.bairro.nome}"
            )

def criar_dados_dashboard():
    """Cria dados adicionais para deixar o dashboard mais interessante"""
    print("\n📈 Criando dados adicionais do dashboard...")
    
    # Atualizar contadores nos usuários
    for usuario in UsuarioApp.objects.all():
        total_relatos = RelatorioAlagamento.objects.filter(usuario=usuario).count()
        total_confirmacoes = InteracaoRelatorio.objects.filter(
            usuario=usuario, tipo='confirmacao'
        ).count()
        
        usuario.total_relatos = total_relatos
        usuario.pontos_contribuicao = total_relatos * 50 + total_confirmacoes * 10
        usuario.save()
    
    print("   ✅ Usuários atualizados")
    
    # Criar algumas estatísticas básicas
    from dashboard.models import EstatisticaDashboard
    from django.db.models import Count, Avg, Sum
    
    # Estatísticas por dia
    relatorios_por_dia = RelatorioAlagamento.objects.extra(
        select={'dia': 'DATE(timestamp)'}
    ).values('dia').annotate(
        total=Count('id'),
        severidade_media=Avg('nivel_severidade'),
        confirmacoes_total=Sum('total_confirmacoes')
    )
    
    for stat in relatorios_por_dia:
        EstatisticaDashboard.objects.get_or_create(
            data_referencia=stat['dia'],
            defaults={
                'total_relatos': stat['total'],
                'severidade_media_dia': stat['severidade_media'] or 0,
                'total_confirmacoes': stat['confirmacoes_total'] or 0,
            }
        )
    
    print("   ✅ Estatísticas criadas")

def main():
    """Executa migração completa"""
    print("🌊 MIGRAÇÃO DE DADOS - SISTEMA WAZE ALAGAMENTOS")
    print("=" * 60)
    
    try:
        popular_bairros()
        usuarios_map = criar_usuarios_anonimos()
        migrar_relatorios_csv() 
        criar_dados_dashboard()
        
        print("\n" + "=" * 60)
        print("✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        
        # Estatísticas finais
        total_relatorios = RelatorioAlagamento.objects.count()
        total_usuarios = UsuarioApp.objects.count()
        total_bairros = Bairro.objects.count()
        total_interacoes = InteracaoRelatorio.objects.count()
        
        print(f"📊 Estatísticas Finais:")
        print(f"   📍 Relatórios: {total_relatorios}")
        print(f"   👥 Usuários: {total_usuarios}")
        print(f"   🏘️ Bairros: {total_bairros}")
        print(f"   💬 Interações: {total_interacoes}")
        
        print(f"\n🚀 Banco populado! Execute: python manage.py runserver")
        
    except Exception as e:
        print(f"❌ Erro durante migração: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()