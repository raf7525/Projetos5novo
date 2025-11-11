"""
Análise Exploratória dos Dados - Sistema Waze de Alagamentos
===========================================================

Este script realiza análise exploratória dos dados de alagamentos em Recife
para desenvolver um sistema colaborativo tipo Waze.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Configuração de estilo
plt.style.use('default')
sns.set_palette("husl")

class FloodDataAnalyzer:
    def __init__(self, data_path):
        """Inicializa o analisador com o caminho dos dados"""
        self.data_path = data_path
        self.df = None
        self.load_data()
        
    def load_data(self):
        """Carrega e realiza limpeza inicial dos dados"""
        try:
            self.df = pd.read_csv(self.data_path)
            print("✅ Dados carregados com sucesso!")
            print(f"📊 Shape: {self.df.shape}")
            print(f"📅 Período: {self.df['timestamp'].min()} até {self.df['timestamp'].max()}")
            
            # Conversão de tipos
            self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
            self.df['nivel_severidade'] = self.df['nivel_severidade'].astype(int)
            self.df['confirmacoes'] = self.df['confirmacoes'].astype(int)
            
            # Criação de colunas derivadas
            self.df['hora'] = self.df['timestamp'].dt.hour
            self.df['dia_semana'] = self.df['timestamp'].dt.day_name()
            self.df['mes'] = self.df['timestamp'].dt.month
            self.df['data'] = self.df['timestamp'].dt.date
            
            print("✅ Transformações aplicadas!")
            
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
    
    def basic_statistics(self):
        """Estatísticas básicas dos dados"""
        print("\n" + "="*60)
        print("📈 ESTATÍSTICAS BÁSICAS")
        print("="*60)
        
        print("\n🔍 Informações Gerais:")
        print(self.df.info())
        
        print("\n📊 Estatísticas Descritivas:")
        numeric_cols = ['nivel_severidade', 'confirmacoes', 'latitude', 'longitude']
        print(self.df[numeric_cols].describe())
        
        print("\n🏘️ Distribuição por Bairro:")
        bairro_stats = self.df['bairro'].value_counts()
        print(bairro_stats)
        
        print("\n⚠️ Distribuição de Severidade:")
        severidade_stats = self.df['nivel_severidade'].value_counts().sort_index()
        for nivel, count in severidade_stats.items():
            emoji = {1: "🟢", 2: "🟡", 3: "🟠", 4: "🔴"}[nivel]
            print(f"{emoji} Nível {nivel}: {count} relatos ({count/len(self.df)*100:.1f}%)")
    
    def data_quality_check(self):
        """Verifica qualidade e integridade dos dados"""
        print("\n" + "="*60)
        print("🔍 ANÁLISE DE QUALIDADE DOS DADOS")
        print("="*60)
        
        # Valores nulos
        print("\n📋 Valores Nulos:")
        null_counts = self.df.isnull().sum()
        for col, nulls in null_counts.items():
            if nulls > 0:
                print(f"❌ {col}: {nulls} valores nulos ({nulls/len(self.df)*100:.1f}%)")
        if null_counts.sum() == 0:
            print("✅ Nenhum valor nulo encontrado!")
        
        # Duplicatas
        duplicates = self.df.duplicated().sum()
        print(f"\n🔄 Registros Duplicados: {duplicates}")
        
        # Outliers geográficos (coordenadas de Recife)
        lat_bounds = (-8.2, -7.9)  # Aproximadamente os limites de Recife
        lon_bounds = (-35.0, -34.8)
        
        outliers_lat = ((self.df['latitude'] < lat_bounds[0]) | 
                       (self.df['latitude'] > lat_bounds[1])).sum()
        outliers_lon = ((self.df['longitude'] < lon_bounds[0]) | 
                       (self.df['longitude'] > lon_bounds[1])).sum()
        
        print(f"\n🗺️ Outliers Geográficos:")
        print(f"   Latitude fora de {lat_bounds}: {outliers_lat}")
        print(f"   Longitude fora de {lon_bounds}: {outliers_lon}")
        
        # Consistência de severidade
        print(f"\n⚠️ Análise de Severidade:")
        print(f"   Valores únicos: {sorted(self.df['nivel_severidade'].unique())}")
        invalid_severity = ((self.df['nivel_severidade'] < 1) | 
                            (self.df['nivel_severidade'] > 4)).sum()
        print(f"   Níveis inválidos (fora de 1-4): {invalid_severity}")
    
    def temporal_analysis(self):
        """Análise temporal dos alagamentos"""
        print("\n" + "="*60)
        print("⏰ ANÁLISE TEMPORAL")
        print("="*60)
        
        # Por hora do dia
        print("\n🕐 Distribuição por Hora:")
        hourly = self.df.groupby('hora').size()
        peak_hour = hourly.idxmax()
        print(f"   Pico de ocorrências: {peak_hour}h ({hourly[peak_hour]} relatos)")
        
        # Por dia da semana
        print("\n📅 Distribuição por Dia da Semana:")
        weekly = self.df['dia_semana'].value_counts()
        for day, count in weekly.items():
            print(f"   {day}: {count} relatos")
        
        # Tendência temporal
        daily_counts = self.df.groupby('data').size()
        print(f"\n📈 Tendência Temporal:")
        print(f"   Período de análise: {daily_counts.index.min()} a {daily_counts.index.max()}")
        print(f"   Média diária: {daily_counts.mean():.1f} relatos")
        print(f"   Dia com mais relatos: {daily_counts.idxmax()} ({daily_counts.max()} relatos)")
    
    def severity_analysis(self):
        """Análise detalhada de severidade"""
        print("\n" + "="*60)
        print("⚠️ ANÁLISE DE SEVERIDADE")
        print("="*60)
        
        # Correlação severidade vs confirmações
        correlation = self.df['nivel_severidade'].corr(self.df['confirmacoes'])
        print(f"\n🔗 Correlação Severidade × Confirmações: {correlation:.3f}")
        
        # Severidade por bairro
        print("\n🏘️ Severidade Média por Bairro:")
        bairro_severity = self.df.groupby('bairro').agg({
            'nivel_severidade': ['mean', 'count'],
            'confirmacoes': 'mean'
        }).round(2)
        
        bairro_severity.columns = ['Severidade_Média', 'Total_Relatos', 'Confirmações_Média']
        bairro_severity = bairro_severity.sort_values('Severidade_Média', ascending=False)
        
        for bairro, row in bairro_severity.head().iterrows():
            print(f"   {bairro}: {row['Severidade_Média']:.2f} "
                  f"({row['Total_Relatos']} relatos, {row['Confirmações_Média']:.1f} conf./relato)")
    
    def user_engagement_analysis(self):
        """Análise do engajamento dos usuários"""
        print("\n" + "="*60)
        print("👥 ANÁLISE DE ENGAJAMENTO")
        print("="*60)
        
        # Usuários mais ativos
        user_activity = self.df['id_usuario'].value_counts()
        print(f"\n🏆 Top 5 Usuários Mais Ativos:")
        for i, (user, posts) in enumerate(user_activity.head().items(), 1):
            print(f"   {i}. {user}: {posts} relatos")
        
        # Distribuição de confirmações
        print(f"\n✅ Estatísticas de Confirmações:")
        conf_stats = self.df['confirmacoes'].describe()
        print(f"   Média: {conf_stats['mean']:.1f}")
        print(f"   Mediana: {conf_stats['50%']:.1f}")
        print(f"   Máximo: {conf_stats['max']:.0f}")
        
        # Relatos sem confirmação
        zero_conf = (self.df['confirmacoes'] == 0).sum()
        print(f"   Relatos sem confirmação: {zero_conf} ({zero_conf/len(self.df)*100:.1f}%)")
    
    def generate_insights_report(self):
        """Gera relatório de insights para o sistema"""
        print("\n" + "="*80)
        print("💡 INSIGHTS PARA O SISTEMA TIPO WAZE")
        print("="*80)
        
        insights = []
        
        # Insight 1: Padrões temporais
        hourly = self.df.groupby('hora').size()
        peak_hours = hourly.nlargest(3).index.tolist()
        insights.append(f"🕐 Implementar notificações proativas nos horários de pico: {peak_hours}")
        
        # Insight 2: Bairros críticos
        critical_areas = self.df[self.df['nivel_severidade'] >= 3]['bairro'].value_counts().head(3).index.tolist()
        insights.append(f"🚨 Foco em monitoramento intensivo em: {', '.join(critical_areas)}")
        
        # Insight 3: Sistema de gamificação
        avg_confirmations = self.df['confirmacoes'].mean()
        insights.append(f"🎮 Sistema de pontos baseado em confirmações (média atual: {avg_confirmations:.1f})")
        
        # Insight 4: Validação automática
        high_conf_threshold = self.df['confirmacoes'].quantile(0.75)
        insights.append(f"✅ Auto-validação para relatos com >{high_conf_threshold:.0f} confirmações")
        
        for i, insight in enumerate(insights, 1):
            print(f"{i}. {insight}")
    
    def export_processed_data(self):
        """Exporta dados processados para uso no dashboard"""
        try:
            # Dados agregados por bairro
            bairro_agg = self.df.groupby('bairro').agg({
                'nivel_severidade': ['mean', 'count'],
                'confirmacoes': 'sum',
                'latitude': 'mean',
                'longitude': 'mean'
            }).round(4)
            
            bairro_agg.columns = ['severidade_media', 'total_relatos', 'total_confirmacoes', 'lat_centro', 'lon_centro']
            bairro_agg.to_csv('data/processed/bairros_agregados.csv')
            
            # Dados temporais
            temporal_data = self.df.groupby([self.df['timestamp'].dt.date, 'hora']).size().reset_index()
            temporal_data.columns = ['data', 'hora', 'total_relatos']
            temporal_data.to_csv('data/processed/temporal_data.csv', index=False)
            
            print("✅ Dados processados exportados com sucesso!")
            
        except Exception as e:
            print(f"❌ Erro ao exportar: {e}")

class DataAnalyzer:
    """Utilities for data analysis and statistics - Mantida compatibilidade"""
    
    @staticmethod
    def basic_stats(df):
        """Get basic statistical information"""
        return {
            'shape': df.shape,
            'describe': df.describe().to_dict(),
            'data_types': df.dtypes.to_dict(),
            'missing_values': df.isnull().sum().to_dict()
        }
    
    @staticmethod
    def correlation_matrix(df, numeric_only=True):
        """Calculate correlation matrix for numeric columns"""
        if numeric_only:
            numeric_df = df.select_dtypes(include=[np.number])
            return numeric_df.corr()
        return df.corr()
    
    @staticmethod
    def value_counts_analysis(df, column):
        """Analyze value counts for a specific column"""
        return {
            'value_counts': df[column].value_counts().to_dict(),
            'unique_count': df[column].nunique(),
            'most_frequent': df[column].mode().iloc[0] if not df[column].mode().empty else None
        }
    
    @staticmethod
    def detect_numeric_columns(df):
        """Detect numeric columns in dataframe"""
        return df.select_dtypes(include=[np.number]).columns.tolist()
    
    @staticmethod
    def detect_categorical_columns(df):
        """Detect categorical columns in dataframe"""
        return df.select_dtypes(include=['object', 'category']).columns.tolist()

def main():
    """Função principal de análise"""
    print("🌊 SISTEMA DE ANÁLISE DE ALAGAMENTOS - RECIFE")
    print("="*60)
    print("Análise para desenvolvimento de aplicativo tipo Waze")
    print("="*60)
    
    # Inicializar análise
    analyzer = FloodDataAnalyzer('data/raw/data.csv')
    
    # Executar análises
    analyzer.basic_statistics()
    analyzer.data_quality_check()
    analyzer.temporal_analysis()
    analyzer.severity_analysis()
    analyzer.user_engagement_analysis()
    analyzer.generate_insights_report()
    analyzer.export_processed_data()
    
    print("\n✅ Análise concluída! Dados prontos para dashboard e ML.")

if __name__ == "__main__":
    main()