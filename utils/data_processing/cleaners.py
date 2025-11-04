"""
Data cleaning utilities
"""
import pandas as pd
import numpy as np

class DataCleaner:
    """Utilities for cleaning and preprocessing data"""
    
    @staticmethod
    def remove_duplicates(df):
        """Remove duplicate rows"""
        return df.drop_duplicates()
    
    @staticmethod
    def handle_missing_values(df, strategy='drop', fill_value=None):
        """Handle missing values with different strategies"""
        if strategy == 'drop':
            return df.dropna()
        elif strategy == 'fill':
            return df.fillna(fill_value)
        elif strategy == 'forward_fill':
            return df.fillna(method='ffill')
        elif strategy == 'backward_fill':
            return df.fillna(method='bfill')
        else:
            raise ValueError("Strategy must be 'drop', 'fill', 'forward_fill', or 'backward_fill'")
    
    @staticmethod
    def standardize_columns(df):
        """Standardize column names (lowercase, underscores)"""
        df.columns = df.columns.str.lower().str.replace(' ', '_').str.replace('-', '_')
        return df
    
    @staticmethod
    def remove_outliers(df, column, method='iqr', factor=1.5):
        """Remove outliers using IQR method"""
        if method == 'iqr':
            Q1 = df[column].quantile(0.25)
            Q3 = df[column].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - factor * IQR
            upper_bound = Q3 + factor * IQR
            return df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]
        else:
            raise ValueError("Currently only 'iqr' method is supported")