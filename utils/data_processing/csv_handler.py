"""
CSV Handler for data processing
"""
import pandas as pd
import numpy as np
from pathlib import Path
from django.conf import settings

class CSVHandler:
    """Handler for CSV file operations"""
    
    def __init__(self):
        self.data_dir = Path(settings.BASE_DIR) / 'data' / 'raw'
        self.processed_dir = Path(settings.BASE_DIR) / 'data' / 'processed'
        
    def load_data(self, filename):
        """Load CSV data from raw directory"""
        filepath = self.data_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"File {filename} not found in {self.data_dir}")
        return pd.read_csv(filepath)
    
    def preview_data(self, filename, rows=5):
        """Preview first rows of CSV data"""
        df = self.load_data(filename)
        return df.head(rows)
    
    def get_data_info(self, filename):
        """Get basic information about the dataset"""
        df = self.load_data(filename)
        return {
            'shape': df.shape,
            'columns': df.columns.tolist(),
            'dtypes': df.dtypes.to_dict(),
            'null_counts': df.isnull().sum().to_dict()
        }
    
    def save_processed_data(self, dataframe, filename):
        """Save processed data to processed directory"""
        filepath = self.processed_dir / filename
        dataframe.to_csv(filepath, index=False)
        return filepath