"""
Cria dataset sintético de alagamentos baseado nos dados INMET
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def create_synthetic_flood_data():
    """Cria dados sintéticos de alagamentos com base nos insights do INMET"""
    
    print("🌧️ CRIANDO DATASET SINTÉTICO DE ALAGAMENTOS")
    print("=" * 50)
    
    # Configuração de dados baseados na análise INMET
    n_records = 150  # Mais registros para melhor análise
    
    # Baseado nos dados reais: precipitação máxima foi 59.8mm
    # Criar eventos de alagamento correlacionados com precipitação
    
    np.random.seed(42)  # Reprodutibilidade
    
    data_records = []
    
    # Período: últimos 6 meses
    start_date = datetime(2025, 5, 1)
    
    for i in range(n_records):
        # Data aleatória nos últimos 6 meses
        days_offset = np.random.randint(0, 180)
        date = start_date + timedelta(days=days_offset)
        
        # Hora: picos de chuva geralmente à tarde/noite
        hour_weights = [1, 1, 1, 1, 1, 2, 3, 4, 5, 5, 4, 3, 5, 8, 10, 12, 15, 12, 8, 5, 4, 3, 2, 1]
        hour = np.random.choice(24, p=np.array(hour_weights)/sum(hour_weights))
        
        datetime_full = date.replace(hour=hour, minute=np.random.choice([0, 15, 30, 45]))
        
        # Precipitação baseada nos dados INMET analisados
        # Eventos de 0 a 60mm (máximo observado: 59.8mm)
        precip_type = np.random.choice(['sem_chuva', 'leve', 'moderada', 'forte', 'extrema'], 
                                     p=[0.1, 0.3, 0.35, 0.2, 0.05])
        
        if precip_type == 'sem_chuva':
            precipitacao = np.random.uniform(0, 1)
            severidade = 1
        elif precip_type == 'leve':
            precipitacao = np.random.uniform(1, 8)
            severidade = np.random.choice([1, 2], p=[0.7, 0.3])
        elif precip_type == 'moderada':
            precipitacao = np.random.uniform(8, 20)
            severidade = np.random.choice([2, 3], p=[0.6, 0.4])
        elif precip_type == 'forte':
            precipitacao = np.random.uniform(20, 40)
            severidade = np.random.choice([3, 4], p=[0.5, 0.5])
        else:  # extrema
            precipitacao = np.random.uniform(40, 60)
            severidade = 4
        
        # Número de confirmações correlacionado com severidade e precipitação
        base_confirmacoes = max(1, int(precipitacao / 5))
        confirmacoes = max(1, base_confirmacoes + np.random.randint(-2, 4))
        
        # Localização: expandir para várias cidades baseadas nos dados INMET
        cidades_data = [
            {'cidade': 'Brasília', 'uf': 'DF', 'lat': -15.78, 'lon': -47.92},
            {'cidade': 'Goiânia', 'uf': 'GO', 'lat': -16.64, 'lon': -49.25},
            {'cidade': 'Campo Grande', 'uf': 'MS', 'lat': -20.44, 'lon': -54.64},
            {'cidade': 'Cuiabá', 'uf': 'MT', 'lat': -15.60, 'lon': -56.10},
            {'cidade': 'Salvador', 'uf': 'BA', 'lat': -12.97, 'lon': -38.51},
            {'cidade': 'Belo Horizonte', 'uf': 'MG', 'lat': -19.92, 'lon': -43.94},
            {'cidade': 'São Paulo', 'uf': 'SP', 'lat': -23.55, 'lon': -46.64},
            {'cidade': 'Recife', 'uf': 'PE', 'lat': -8.05, 'lon': -34.88},
        ]
        
        cidade_info = np.random.choice(cidades_data)
        
        # Bairros por cidade (exemplos)
        bairros_por_cidade = {
            'Brasília': ['Asa Norte', 'Asa Sul', 'Lago Norte', 'Lago Sul', 'Taguatinga', 'Ceilândia'],
            'Goiânia': ['Centro', 'Setor Oeste', 'Jardim América', 'Vila Nova', 'Campinas'],
            'Campo Grande': ['Centro', 'Tiradentes', 'Aero Rancho', 'Coophavila II'],
            'Cuiabá': ['Centro', 'Goiabeiras', 'Jardim Europa', 'Coxipó'],
            'Salvador': ['Pelourinho', 'Barra', 'Campo Grande', 'Itapuã', 'Liberdade'],
            'Belo Horizonte': ['Centro', 'Savassi', 'Funcionários', 'Pampulha', 'Barreiro'],
            'São Paulo': ['Centro', 'Vila Madalena', 'Itaim', 'Mooca', 'Tatuapé'],
            'Recife': ['Boa Viagem', 'Espinheiro', 'Graças', 'Imbiribeira', 'Varzea']
        }
        
        bairro = np.random.choice(bairros_por_cidade.get(cidade_info['cidade'], ['Centro']))
        
        # Coordenadas com pequena variação
        lat = cidade_info['lat'] + np.random.uniform(-0.1, 0.1)
        lon = cidade_info['lon'] + np.random.uniform(-0.1, 0.1)
        
        # Descrições baseadas na severidade
        descricoes = {
            1: ["Poça d'água na rua", "Leve alagamento na calçada", "Água acumulada em bueiro"],
            2: ["Alagamento moderado na via", "Água cobrindo meio-fio", "Trânsito lento por água"],
            3: ["Alagamento significativo", "Carros com dificuldade", "Água até o joelho"],
            4: ["Alagamento crítico", "Carros ilhados", "Água muito alta", "Situação perigosa"]
        }
        
        descricao_base = np.random.choice(descricoes[severidade])
        if precipitacao > 0:
            descricao = f"{descricao_base} - Precipitação: {precipitacao:.1f}mm"
        else:
            descricao = descricao_base
        
        # Usuario
        usuario = f"user_{np.random.randint(1000, 9999)}"
        
        data_records.append({
            'data': datetime_full.strftime('%Y-%m-%d %H:%M:%S'),
            'cidade': cidade_info['cidade'],
            'uf': cidade_info['uf'],
            'bairro': bairro,
            'latitude': round(lat, 6),
            'longitude': round(lon, 6),
            'severidade': severidade,
            'confirmacoes': confirmacoes,
            'usuario': usuario,
            'descricao': descricao,
            'precipitacao_mm': round(precipitacao, 1),
            'categoria_chuva': precip_type
        })
    
    # Criar DataFrame
    df = pd.DataFrame(data_records)
    
    # Salvar
    output_path = "/home/raf75/quinto-periodo/projetos/Projetos5novo/data/raw/alagamentos_inmet_synthetic.csv"
    df.to_csv(output_path, index=False, encoding='utf-8')
    
    print(f"💾 Dataset criado: {output_path}")
    print(f"📊 {len(df)} registros de alagamento")
    
    # Estatísticas
    print("\n📈 ESTATÍSTICAS DO DATASET:")
    print(f"   Período: {df['data'].min()} até {df['data'].max()}")
    print(f"   Precipitação máxima: {df['precipitacao_mm'].max():.1f}mm")
    print(f"   Precipitação média: {df['precipitacao_mm'].mean():.1f}mm")
    
    print("\n🌧️ DISTRIBUIÇÃO POR SEVERIDADE:")
    sev_counts = df['severidade'].value_counts().sort_index()
    labels = {1: 'Baixo', 2: 'Moderado', 3: 'Alto', 4: 'Crítico'}
    for sev, count in sev_counts.items():
        percentage = (count/len(df))*100
        print(f"   {labels[sev]}: {count} casos ({percentage:.1f}%)")
    
    print("\n🏙️ DISTRIBUIÇÃO POR CIDADE:")
    city_counts = df['cidade'].value_counts()
    for city, count in city_counts.head().items():
        print(f"   {city}: {count} relatórios")
    
    print("\n☔ CATEGORIA DE CHUVA:")
    cat_counts = df['categoria_chuva'].value_counts()
    for cat, count in cat_counts.items():
        percentage = (count/len(df))*100
        print(f"   {cat.title()}: {count} eventos ({percentage:.1f}%)")
    
    return output_path

if __name__ == "__main__":
    create_synthetic_flood_data()