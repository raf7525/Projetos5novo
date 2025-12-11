import os
import joblib
import pandas as pd
import numpy as np
from django.conf import settings
from utils.ml_classifier import FloodSeverityClassifier

class FloodPredictor:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        self.classifier = FloodSeverityClassifier(data_path=None)
        self.model_path = os.path.join(settings.BASE_DIR, 'data', 'models')
        self.is_loaded = self.classifier.load_model(self.model_path)
        
    def predict(self, latitude, longitude, timestamp, confirmacoes, bairro):
        """
        Realiza predição de severidade
        """
        if not self.is_loaded:
            # Tenta carregar novamente
            self.is_loaded = self.classifier.load_model(self.model_path)
            if not self.is_loaded:
                return None
                
        data = {
            'latitude': float(latitude),
            'longitude': float(longitude),
            'timestamp': timestamp,
            'confirmacoes': int(confirmacoes),
            'bairro': str(bairro)
        }
        
        return self.classifier.predict_severity(data)

def predict_flood_severity(latitude, longitude, timestamp, confirmacoes, bairro):
    """Função helper para uso direto"""
    predictor = FloodPredictor.get_instance()
    return predictor.predict(latitude, longitude, timestamp, confirmacoes, bairro)
