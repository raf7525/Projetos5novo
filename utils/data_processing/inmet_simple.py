"""
Processador simplificado para dados INMET
Foca em precipitação para predição de alagamentos
"""
import pandas as pd
import numpy as np
import os
import glob

def find_inmet_files(base_path="/home/raf75/quinto-periodo/projetos"):
    """Encontra arquivos INMET"""
    pattern = f"{base_path}/**/INMET_*.CSV"
    files = glob.glob(pattern, recursive=True)
    return files[:10]  # Primeiros 10 para teste

def analyze_single_file(filepath):
    """Analisa um arquivo INMET"""
    try:
        print(f"\n📊 Analisando: {os.path.basename(filepath)}")
        
        # Carregar só para ver colunas
        df_sample = pd.read_csv(filepath, sep=';', skiprows=8, nrows=5, encoding='latin-1')
        print(f"🔍 Colunas encontradas:")
        for i, col in enumerate(df_sample.columns):
            print(f"   {i}: {col.strip()}")
        
        # Carregar dados completos
        df = pd.read_csv(
            filepath, 
            sep=';', 
            skiprows=8,
            encoding='latin-1',
            na_values=['-9999', '', ' ']
        )
        
        # Limpar nomes
        df.columns = df.columns.str.strip()
        
        # Procurar coluna de precipitação
        precip_col = None
        for col in df.columns:
            if 'PRECIPITA' in col.upper():
                precip_col = col
                break
        
        if precip_col:
            print(f"✅ Coluna precipitação: {precip_col}")
            
            # Converter para numérico
            df[precip_col] = pd.to_numeric(
                df[precip_col].astype(str).str.replace(',', '.'), 
                errors='coerce'
            )
            
            # Estatísticas
            precip_stats = df[precip_col].describe()
            print(f"📈 Precipitação - Máx: {precip_stats['max']:.2f}mm, Média: {precip_stats['mean']:.2f}mm")
            
            # Eventos de chuva significativa
            heavy_rain = df[df[precip_col] > 20]
            print(f"🌧️ Chuvas >20mm: {len(heavy_rain)} eventos")
            
            return {
                'file': filepath,
                'records': len(df),
                'precip_col': precip_col,
                'max_precip': precip_stats['max'],
                'heavy_events': len(heavy_rain),
                'data': df[[col for col in ['DATA (YYYY-MM-DD)', 'HORA (UTC)', precip_col] if col in df.columns]]
            }
        else:
            print("❌ Coluna de precipitação não encontrada")
            return None
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

def create_flood_dataset():
    """Cria dataset de risco de alagamento"""
    print("🌧️ CRIANDO DATASET DE ALAGAMENTOS")
    print("=" * 50)
    
    files = find_inmet_files()
    print(f"📁 Processando {len(files)} arquivos...")
    
    all_data = []
    
    for filepath in files:
        result = analyze_single_file(filepath)
        if result:
            all_data.append(result)
    
    if all_data:
        print(f"\n✅ {len(all_data)} arquivos processados com sucesso!")
        
        # Combinar dados
        combined_records = sum(item['records'] for item in all_data)
        max_precipitation = max(item['max_precip'] for item in all_data)
        total_heavy_events = sum(item['heavy_events'] for item in all_data)
        
        print(f"📊 RESUMO GERAL:")
        print(f"   Total registros: {combined_records:,}")
        print(f"   Precipitação máxima: {max_precipitation:.1f}mm")
        print(f"   Eventos chuva pesada (>20mm): {total_heavy_events}")
        
        # Criar DataFrame simplificado para integração
        sample_data = []
        
        for item in all_data[:3]:  # Usar dados de 3 arquivos
            df = item['data']
            if len(df) > 0 and item['precip_col'] in df.columns:
                
                # Extrair dados relevantes
                for idx, row in df.head(100).iterrows():  # 100 registros por arquivo
                    try:
                        data_str = row.get('DATA (YYYY-MM-DD)', '')
                        hora_str = row.get('HORA (UTC)', '00:00')
                        precip = row.get(item['precip_col'], 0)
                        
                        if pd.notna(precip) and precip > 0:
                            # Simular dados de alagamento baseados em precipitação
                            if precip > 30:
                                severidade = 4  # Crítico
                                confirmacoes = np.random.randint(8, 15)
                            elif precip > 15:
                                severidade = 3  # Alto
                                confirmacoes = np.random.randint(5, 10)
                            elif precip > 5:
                                severidade = 2  # Moderado
                                confirmacoes = np.random.randint(2, 7)
                            else:
                                severidade = 1  # Baixo
                                confirmacoes = np.random.randint(1, 4)
                            
                            # Coordenadas de exemplo (Brasília e região)
                            lat = -15.7801 + np.random.uniform(-0.5, 0.5)
                            lon = -47.9292 + np.random.uniform(-0.5, 0.5)
                            
                            bairros = ['Asa Norte', 'Asa Sul', 'Lago Norte', 'Lago Sul', 
                                     'Taguatinga', 'Ceilândia', 'Samambaia', 'Gama', 
                                     'Santa Maria', 'Recanto das Emas']
                            
                            sample_data.append({
                                'data': f"{data_str} {hora_str}",
                                'bairro': np.random.choice(bairros),
                                'latitude': lat,
                                'longitude': lon,
                                'severidade': severidade,
                                'confirmacoes': confirmacoes,
                                'usuario': f'user_{np.random.randint(100, 999)}',
                                'descricao': f'Alagamento reportado - Precipitação: {precip:.1f}mm',
                                'precipitacao_mm': precip
                            })
                            
                    except Exception as e:
                        continue
        
        # Criar DataFrame final
        if sample_data:
            df_final = pd.DataFrame(sample_data)
            
            # Salvar
            output_path = "/home/raf75/quinto-periodo/projetos/Projetos5novo/data/raw/alagamentos_inmet.csv"
            df_final.to_csv(output_path, index=False)
            
            print(f"\n💾 Dataset criado: {output_path}")
            print(f"📊 {len(df_final)} registros de alagamento baseados em precipitação")
            print(f"🌧️ Distribuição por severidade:")
            
            sev_counts = df_final['severidade'].value_counts().sort_index()
            labels = {1: 'Baixo', 2: 'Moderado', 3: 'Alto', 4: 'Crítico'}
            for sev, count in sev_counts.items():
                print(f"   {labels[sev]}: {count} casos")
                
            return output_path
        
    return None

if __name__ == "__main__":
    create_flood_dataset()