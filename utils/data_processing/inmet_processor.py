"""
Processador de dados meteorológicos INMET
Integra dados de precipitação para predição de alagamentos
"""
import pandas as pd
import numpy as np
from datetime import datetime
import os
import glob
from pathlib import Path

class INMETProcessor:
    """
    Processador para dados meteorológicos do INMET
    Foco em precipitação para predição de alagamentos
    """
    
    def __init__(self, data_dir="/home/raf75/quinto-periodo/projetos"):
        self.data_dir = data_dir
        self.processed_data = None
        
    def find_inmet_files(self):
        """
        Encontra todos os arquivos CSV do INMET
        """
        pattern = f"{self.data_dir}/**/INMET_*.CSV"
        files = glob.glob(pattern, recursive=True)
        print(f"📁 Encontrados {len(files)} arquivos INMET")
        return files
    
    def parse_inmet_header(self, filepath):
        """
        Extrai metadados do cabeçalho INMET
        """
        metadata = {}
        with open(filepath, 'r', encoding='latin-1') as f:
            for i, line in enumerate(f):
                if i > 10:  # Após cabeçalho
                    break
                    
                if ':' in line and 'DATA' not in line:
                    parts = line.strip().split(':')
                    if len(parts) >= 2:
                        key = parts[0].replace('�', '').strip()
                        value = parts[1].strip().rstrip(';')
                        metadata[key] = value
        
        return metadata
    
    def load_single_file(self, filepath):
        """
        Carrega um arquivo INMET específico
        """
        try:
            print(f"📊 Processando: {os.path.basename(filepath)}")
            
            # Extrair metadados
            metadata = self.parse_inmet_header(filepath)
            
            # Carregar dados (pular cabeçalho)
            df = pd.read_csv(
                filepath, 
                sep=';', 
                skiprows=8,  # Pular cabeçalho de metadados
                encoding='latin-1',
                na_values=['-9999', '', ' ']
            )
            
            # Limpar nomes das colunas
            df.columns = df.columns.str.strip()
            
            # Renomear colunas principais
            column_mapping = {
                'DATA (YYYY-MM-DD)': 'data',
                'HORA (UTC)': 'hora',
                'PRECIPITA��O TOTAL, HOR�RIO (mm)': 'precipitacao_mm',
                'TEMPERATURA DO AR - BULBO SECO, HORARIA (�C)': 'temperatura_c',
                'UMIDADE RELATIVA DO AR, HORARIA (%)': 'umidade_perc',
                'PRESS�O ATMOSFERICA AO NIVEL DA ESTACAO, HORARIA (mB)': 'pressao_mb',
                'VENTO, VELOCIDADE HORARIA (m/s)': 'vento_velocidade',
                'VENTO, DIRE��O HORARIA (gr) (� (gr))': 'vento_direcao'
            }
            
            # Aplicar mapeamento disponível
            for old_name, new_name in column_mapping.items():
                if old_name in df.columns:
                    df.rename(columns={old_name: new_name}, inplace=True)
            
            # Adicionar metadados
            df['estacao'] = metadata.get('ESTA��O', 'UNKNOWN')
            df['codigo_estacao'] = metadata.get('CODIGO (WMO)', 'UNKNOWN')
            
            # Tratar coordenadas que podem ter ';' no início
            lat_str = metadata.get('LATITUDE', '0').replace(',', '.').replace(';', '').strip()
            lon_str = metadata.get('LONGITUDE', '0').replace(',', '.').replace(';', '').strip()
            
            try:
                df['latitude'] = float(lat_str)
                df['longitude'] = float(lon_str)
            except ValueError:
                df['latitude'] = 0.0
                df['longitude'] = 0.0
            
            df['uf'] = metadata.get('UF', 'UNKNOWN')
            
            # Criar datetime
            if 'data' in df.columns and 'hora' in df.columns:
                df['datetime'] = pd.to_datetime(
                    df['data'] + ' ' + df['hora'], 
                    format='%Y-%m-%d %H:%M',
                    errors='coerce'
                )
            
            # Converter precipitação para numérico
            if 'precipitacao_mm' in df.columns:
                df['precipitacao_mm'] = pd.to_numeric(
                    df['precipitacao_mm'].astype(str).str.replace(',', '.'), 
                    errors='coerce'
                )
            
            print(f"✅ Carregado: {len(df)} registros de {metadata.get('ESTA��O', 'UNKNOWN')}")
            return df
            
        except Exception as e:
            print(f"❌ Erro ao processar {filepath}: {e}")
            return None
    
    def process_all_files(self):
        """
        Processa todos os arquivos INMET encontrados
        """
        files = self.find_inmet_files()
        
        if not files:
            print("❌ Nenhum arquivo INMET encontrado!")
            return None
        
        dataframes = []
        
        for file in files[:5]:  # Processar primeiros 5 para teste
            df = self.load_single_file(file)
            if df is not None:
                dataframes.append(df)
        
        if dataframes:
            # Combinar todos os dataframes
            self.processed_data = pd.concat(dataframes, ignore_index=True)
            print("\n🎯 RESUMO FINAL:")
            print(f"📊 Total de registros: {len(self.processed_data)}")
            print(f"📅 Período: {self.processed_data['datetime'].min()} até {self.processed_data['datetime'].max()}")
            print(f"🌧️ Precipitação máxima: {self.processed_data['precipitacao_mm'].max():.1f}mm")
            
            return self.processed_data
        
        return None
    
    def analyze_precipitation_patterns(self):
        """
        Análise de padrões de precipitação para alagamentos
        """
        if self.processed_data is None:
            print("❌ Carregue os dados primeiro!")
            return
        
        df = self.processed_data.copy()
        
        print("\n🌧️ ANÁLISE DE PRECIPITAÇÃO:")
        
        # Estatísticas básicas
        precip_stats = df['precipitacao_mm'].describe()
        print(f"📊 Estatísticas de precipitação (mm):")
        print(f"   Média: {precip_stats['mean']:.2f}mm")
        print(f"   Máximo: {precip_stats['max']:.2f}mm")
        print(f"   75º percentil: {precip_stats['75%']:.2f}mm")
        
        # Eventos extremos (potenciais alagamentos)
        threshold_light = 5.0   # Chuva leve
        threshold_moderate = 15.0  # Chuva moderada  
        threshold_heavy = 30.0  # Chuva forte (risco alto alagamento)
        
        events = {
            'sem_chuva': len(df[df['precipitacao_mm'] <= 0]),
            'chuva_leve': len(df[(df['precipitacao_mm'] > 0) & (df['precipitacao_mm'] <= threshold_light)]),
            'chuva_moderada': len(df[(df['precipitacao_mm'] > threshold_light) & (df['precipitacao_mm'] <= threshold_moderate)]),
            'chuva_forte': len(df[(df['precipitacao_mm'] > threshold_moderate) & (df['precipitacao_mm'] <= threshold_heavy)]),
            'chuva_extrema': len(df[df['precipitacao_mm'] > threshold_heavy])
        }
        
        print(f"\n📈 CATEGORIZAÇÃO DOS EVENTOS:")
        for category, count in events.items():
            percentage = (count/len(df))*100
            print(f"   {category.replace('_', ' ').title()}: {count} eventos ({percentage:.1f}%)")
        
        return events
    
    def create_flood_risk_features(self):
        """
        Cria features de risco de alagamento baseadas em precipitação
        """
        if self.processed_data is None:
            return None
        
        df = self.processed_data.copy()
        
        # Features temporais
        df['hora'] = df['datetime'].dt.hour
        df['dia_semana'] = df['datetime'].dt.dayofweek
        df['mes'] = df['datetime'].dt.month
        
        # Features de precipitação
        df['precipitacao_categoria'] = pd.cut(
            df['precipitacao_mm'], 
            bins=[-np.inf, 0, 5, 15, 30, np.inf],
            labels=['sem_chuva', 'leve', 'moderada', 'forte', 'extrema']
        )
        
        # Precipitação acumulada (janelas de tempo)
        df = df.sort_values('datetime')
        df['precip_3h'] = df['precipitacao_mm'].rolling(window=3, min_periods=1).sum()
        df['precip_6h'] = df['precipitacao_mm'].rolling(window=6, min_periods=1).sum()
        df['precip_24h'] = df['precipitacao_mm'].rolling(window=24, min_periods=1).sum()
        
        # Risco de alagamento (baseado em acumulado)
        df['risco_alagamento'] = np.select([
            df['precip_24h'] <= 10,
            (df['precip_24h'] > 10) & (df['precip_24h'] <= 30),
            (df['precip_24h'] > 30) & (df['precip_24h'] <= 50),
            df['precip_24h'] > 50
        ], [1, 2, 3, 4], default=1)  # 1=baixo, 4=crítico
        
        self.processed_data = df
        
        print("✅ Features de risco de alagamento criadas!")
        print(f"📊 Distribuição de risco:")
        risk_dist = df['risco_alagamento'].value_counts().sort_index()
        for risk, count in risk_dist.items():
            labels = {1: 'Baixo', 2: 'Moderado', 3: 'Alto', 4: 'Crítico'}
            print(f"   Risco {labels[risk]}: {count} registros")
        
        return df
    
    def export_for_django(self, output_path=None):
        """
        Exporta dados processados para integração com Django
        """
        if self.processed_data is None:
            print("❌ Processe os dados primeiro!")
            return
        
        if output_path is None:
            output_path = "/home/raf75/quinto-periodo/projetos/Projetos5novo/data/raw/inmet_processed.csv"
        
        # Selecionar colunas relevantes
        columns_to_export = [
            'datetime', 'data', 'hora', 'precipitacao_mm',
            'temperatura_c', 'umidade_perc', 'pressao_mb',
            'latitude', 'longitude', 'estacao', 'uf',
            'precipitacao_categoria', 'precip_3h', 'precip_6h', 'precip_24h',
            'risco_alagamento'
        ]
        
        # Filtrar colunas que existem
        available_columns = [col for col in columns_to_export if col in self.processed_data.columns]
        
        export_df = self.processed_data[available_columns].copy()
        
        # Remover registros com datetime inválido
        export_df = export_df.dropna(subset=['datetime'])
        
        # Exportar
        export_df.to_csv(output_path, index=False, encoding='utf-8')
        
        print(f"💾 Dados exportados para: {output_path}")
        print(f"📊 {len(export_df)} registros exportados")
        
        return output_path

if __name__ == "__main__":
    # Exemplo de uso
    processor = INMETProcessor()
    
    print("🌦️ PROCESSADOR DE DADOS INMET")
    print("=" * 50)
    
    # Processar arquivos
    data = processor.process_all_files()
    
    if data is not None:
        # Analisar padrões
        processor.analyze_precipitation_patterns()
        
        # Criar features
        processor.create_flood_risk_features()
        
        # Exportar para Django
        processor.export_for_django()
        
        print("\n✅ Processamento completo!")
    else:
        print("❌ Falha no processamento!")