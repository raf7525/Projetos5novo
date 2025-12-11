from django.core.management.base import BaseCommand
from utils.ml_classifier import FloodSeverityClassifier
import os

class Command(BaseCommand):
    help = 'Treina o modelo de Machine Learning para classificação de severidade'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🤖 Iniciando treinamento do modelo ML...'))
        
        data_path = 'data/raw/data.csv'
        
        if not os.path.exists(data_path):
            self.stdout.write(self.style.ERROR(f'❌ Arquivo de dados não encontrado: {data_path}'))
            self.stdout.write('Execute "python manage.py populate_inmet" primeiro para gerar dados.')
            return

        try:
            classifier = FloodSeverityClassifier(data_path)
            
            # Treinar e analisar
            self.stdout.write('📊 Executando análise e treinamento...')
            best_model_name, metrics = classifier.run_complete_analysis()
            
            # Salvar modelo
            self.stdout.write('💾 Salvando modelo e artefatos...')
            classifier.save_model('data/models')
            
            self.stdout.write(self.style.SUCCESS(f'✅ Modelo treinado e salvo com sucesso!'))
            self.stdout.write(f'🏆 Melhor modelo: {best_model_name}')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro durante o treinamento: {str(e)}'))
