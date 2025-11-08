import pandas as pd
import numpy as np

class DataCleaner:
    """ESSE ARQUIVO SERVE PARA LIMPEZA DE DADOS ELE TIRA OUTLIERS E DUPLICATAS"""
    
    @staticmethod
    def remove_duplicates(df):
        """remove linhas duplicadas"""
        return df.drop_duplicates()
    
    @staticmethod
    def handle_missing_values(df, strategy='drop', fill_value=None):
        return df.dropna()
        ##elif strategy == 'fill':
            ##return df.fillna(fill_value)
            ##CASO PRECISE ADICIONAR OUTRAS FORMAS DE LIDAR COM VALORES FALTANTES, PODE ADICIONAR AQUI, SÓ TIRAR O COMENTÁRIO
            
    @staticmethod
    def padroniza_colunas(df):
        """Padroniza os nomes das colunas para minúsculas e substitui espaços por underline"""
        df.columns = df.columns.str.lower().str.replace(' ', '_').str.replace('-', '_')
        return df
    
    @staticmethod
    def remove_outliers(df, column, method='iqr', factor=1.5):
        """Remove outliers usando um método chamado iqr"""
        
        Q1 = df[column].quantile(0.25)##esses valores são o máximo e mínimo aceitáveis, talvez seja necessário mudar diante da necessidade
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        limite_inferior = Q1 - factor * IQR
        limite_maximo = Q3 + factor * IQR
        return df[(df[column] >= limite_inferior) & (df[column] <= limite_maximo)]
    """"Como o iqr funciona, ele define dois limites e todos os valores que estejam
    fora desses limites são considerados outliers e removidos do DataFrame."""