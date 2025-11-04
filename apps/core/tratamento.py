
import sys
import os


sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.data_processing.csv_handler import CSVHandler
from utils.data_processing.cleaners import DataCleaner
from utils.data_processing.analyzers import DataAnalyzer

def main():
    """Função principal para demonstrar o uso das utilities"""
    
    # Inicializar o handler CSV
    csv_handler = CSVHandler()
    
    try:
        # Carregar e visualizar dados
        print("=== CARREGANDO DADOS ===")
        df = csv_handler.load_data('data.csv')
        print("Dados carregados com sucesso!")
        
        # Preview dos dados
        print("\n=== PREVIEW DOS DADOS ===")
        preview = csv_handler.preview_data('data.csv')
        print(preview)
        
        # Análise básica
        print("\n=== INFORMAÇÕES DO DATASET ===")
        info = csv_handler.get_data_info('data.csv')
        print(f"Formato: {info['shape']}")
        print(f"Colunas: {info['columns']}")
        
        # Análise estatística
        print("\n=== ANÁLISE ESTATÍSTICA ===")
        analyzer = DataAnalyzer()
        stats = analyzer.basic_stats(df)
        print(f"Valores ausentes: {stats['missing_values']}")
        
        # Limpeza de dados (exemplo)
        print("\n=== LIMPEZA DE DADOS ===")
        cleaner = DataCleaner()
        df_clean = cleaner.padroniza_colunas(df)
        df_clean = cleaner.remove_duplicates(df_clean)
        print("Dados limpos!")
        
        # Salvar dados processados
        processed_file = csv_handler.save_processed_data(df_clean, 'data_processed.csv')
        print(f"Dados processados salvos em: {processed_file}")
        
    except FileNotFoundError as e:
        print(f"Erro: {e}")
        print("Certifique-se de que o arquivo data.csv está na pasta data/raw/")

if __name__ == "__main__":
    main()

