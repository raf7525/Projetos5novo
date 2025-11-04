"""
Data analysis utilities
"""
import pandas as pd
import numpy as np

class DataAnalyzer:
    """Utilities for data analysis and statistics"""
    
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