"""
Sistema de Machine Learning para Classificação de Severidade de Alagamentos
============================================================================

Implementa classificadores com métricas completas de avaliação:
- Matriz de confusão
- Acurácia, Precisão, Recall, F1-score  
- Curvas ROC e Precision-Recall
- Análise de trade-offs
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    confusion_matrix, classification_report, accuracy_score,
    precision_score, recall_score, f1_score, roc_curve, auc,
    precision_recall_curve, average_precision_score
)
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.pipeline import Pipeline
import warnings
warnings.filterwarnings('ignore')

class FloodSeverityClassifier:
    """Classificador de severidade de alagamentos com análise completa"""
    
    def __init__(self, data_path):
        """Inicializa o classificador"""
        self.data_path = data_path
        self.df = None
        self.X = None
        self.y = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.models = {}
        self.results = {}
        self.scaler = StandardScaler()
        
        self.load_and_prepare_data()
    
    def load_and_prepare_data(self):
        """Carrega e prepara os dados para ML"""
        print("📊 Carregando dados para Machine Learning...")
        
        # Carregar dados
        self.df = pd.read_csv(self.data_path)
        
        # Criar features temporais
        self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
        self.df['hora'] = self.df['timestamp'].dt.hour
        self.df['dia_semana'] = self.df['timestamp'].dt.weekday
        self.df['mes'] = self.df['timestamp'].dt.month
        self.df['eh_fim_semana'] = (self.df['dia_semana'] >= 5).astype(int)
        
        # Encoding de bairros
        le_bairro = LabelEncoder()
        self.df['bairro_encoded'] = le_bairro.fit_transform(self.df['bairro'])
        
        # Criar features derivadas
        self.df['confirmacoes_per_hour'] = self.df['confirmacoes'] / np.maximum((pd.Timestamp.now() - self.df['timestamp']).dt.total_seconds() / 3600, 1)
        self.df['lat_abs'] = np.abs(self.df['latitude'])
        self.df['lon_abs'] = np.abs(self.df['longitude'])
        
        # Definir features e target
        feature_columns = [
            'latitude', 'longitude', 'hora', 'dia_semana', 'mes', 
            'confirmacoes', 'eh_fim_semana', 'bairro_encoded',
            'lat_abs', 'lon_abs'
        ]
        
        self.X = self.df[feature_columns].copy()
        self.y = self.df['nivel_severidade'].copy()
        
        # Split dos dados
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X, self.y, test_size=0.3, random_state=42, stratify=self.y
        )
        
        # Escalar features
        self.X_train_scaled = self.scaler.fit_transform(self.X_train)
        self.X_test_scaled = self.scaler.transform(self.X_test)
        
        print(f"✅ Dados preparados: {self.X.shape[0]} amostras, {self.X.shape[1]} features")
        print(f"📊 Distribuição de classes: {dict(self.y.value_counts().sort_index())}")
    
    def initialize_models(self):
        """Inicializa os modelos de classificação"""
        self.models = {
            'Random Forest': RandomForestClassifier(
                n_estimators=100, random_state=42, max_depth=5
            ),
            'Gradient Boosting': GradientBoostingClassifier(
                random_state=42, max_depth=3, n_estimators=100
            ),
            'SVM': SVC(
                random_state=42, probability=True, kernel='rbf'
            ),
            'Logistic Regression': LogisticRegression(
                random_state=42, max_iter=1000
            )
        }
        print(f"🤖 Modelos inicializados: {list(self.models.keys())}")
    
    def train_and_evaluate(self):
        """Treina e avalia todos os modelos"""
        print("\n🚀 Iniciando treinamento e avaliação dos modelos...")
        
        for name, model in self.models.items():
            print(f"\n📈 Treinando {name}...")
            
            # Treinar modelo
            if name == 'SVM' or name == 'Logistic Regression':
                model.fit(self.X_train_scaled, self.y_train)
                y_pred = model.predict(self.X_test_scaled)
                y_pred_proba = model.predict_proba(self.X_test_scaled)
            else:
                model.fit(self.X_train, self.y_train)
                y_pred = model.predict(self.X_test)
                y_pred_proba = model.predict_proba(self.X_test)
            
            # Calcular métricas
            accuracy = accuracy_score(self.y_test, y_pred)
            precision = precision_score(self.y_test, y_pred, average='weighted')
            recall = recall_score(self.y_test, y_pred, average='weighted')
            f1 = f1_score(self.y_test, y_pred, average='weighted')
            
            # Cross-validation
            if name == 'SVM' or name == 'Logistic Regression':
                cv_scores = cross_val_score(model, self.X_train_scaled, self.y_train, cv=3)
            else:
                cv_scores = cross_val_score(model, self.X_train, self.y_train, cv=3)
            
            # Armazenar resultados
            self.results[name] = {
                'model': model,
                'y_pred': y_pred,
                'y_pred_proba': y_pred_proba,
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std()
            }
            
            print(f"   ✅ Acurácia: {accuracy:.3f}")
            print(f"   ✅ F1-Score: {f1:.3f}")
            print(f"   ✅ CV Score: {cv_scores.mean():.3f} (±{cv_scores.std():.3f})")
    
    def plot_confusion_matrices(self):
        """Plota matrizes de confusão para todos os modelos"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        axes = axes.ravel()
        
        for idx, (name, results) in enumerate(self.results.items()):
            cm = confusion_matrix(self.y_test, results['y_pred'])
            
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                       ax=axes[idx], cbar=True)
            axes[idx].set_title(f'Matriz de Confusão - {name}')
            axes[idx].set_xlabel('Predição')
            axes[idx].set_ylabel('Real')
            axes[idx].set_xticklabels(['Nível 1', 'Nível 2', 'Nível 3', 'Nível 4'])
            axes[idx].set_yticklabels(['Nível 1', 'Nível 2', 'Nível 3', 'Nível 4'])
        
        plt.tight_layout()
        plt.savefig('data/exports/confusion_matrices.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("💾 Matrizes de confusão salvas em 'data/exports/confusion_matrices.png'")
    
    def plot_roc_curves(self):
        """Plota curvas ROC para classificação multiclasse"""
        plt.figure(figsize=(12, 8))
        
        colors = ['blue', 'green', 'red', 'orange']
        
        for idx, (name, results) in enumerate(self.results.items()):
            y_pred_proba = results['y_pred_proba']
            
            # ROC para cada classe (one-vs-rest)
            for class_idx in range(len(np.unique(self.y))):
                # Binarizar para classe atual
                y_binary = (self.y_test == (class_idx + 1)).astype(int)
                
                # Se a classe existe nas predições
                if class_idx < y_pred_proba.shape[1]:
                    fpr, tpr, _ = roc_curve(y_binary, y_pred_proba[:, class_idx])
                    roc_auc = auc(fpr, tpr)
                    
                    plt.plot(fpr, tpr, 
                            color=colors[idx], 
                            linestyle=['-', '--', '-.', ':'][class_idx],
                            label=f'{name} - Classe {class_idx+1} (AUC = {roc_auc:.2f})')
        
        plt.plot([0, 1], [0, 1], 'k--', label='Baseline (AUC = 0.50)')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('Taxa de Falsos Positivos')
        plt.ylabel('Taxa de Verdadeiros Positivos')
        plt.title('Curvas ROC - Classificação Multiclasse')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig('data/exports/roc_curves.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("💾 Curvas ROC salvas em 'data/exports/roc_curves.png'")
    
    def plot_precision_recall_curves(self):
        """Plota curvas Precision-Recall"""
        plt.figure(figsize=(12, 8))
        
        colors = ['blue', 'green', 'red', 'orange']
        
        for idx, (name, results) in enumerate(self.results.items()):
            y_pred_proba = results['y_pred_proba']
            
            for class_idx in range(len(np.unique(self.y))):
                y_binary = (self.y_test == (class_idx + 1)).astype(int)
                
                if class_idx < y_pred_proba.shape[1]:
                    precision, recall, _ = precision_recall_curve(
                        y_binary, y_pred_proba[:, class_idx]
                    )
                    avg_precision = average_precision_score(
                        y_binary, y_pred_proba[:, class_idx]
                    )
                    
                    plt.plot(recall, precision,
                            color=colors[idx],
                            linestyle=['-', '--', '-.', ':'][class_idx],
                            label=f'{name} - Classe {class_idx+1} (AP = {avg_precision:.2f})')
        
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.title('Curvas Precision-Recall')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig('data/exports/precision_recall_curves.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("💾 Curvas Precision-Recall salvas em 'data/exports/precision_recall_curves.png'")
    
    def generate_performance_report(self):
        """Gera relatório detalhado de performance"""
        print("\n" + "="*80)
        print("📊 RELATÓRIO DE PERFORMANCE DOS CLASSIFICADORES")
        print("="*80)
        
        # Criar DataFrame com métricas
        metrics_df = pd.DataFrame({
            'Modelo': list(self.results.keys()),
            'Acurácia': [r['accuracy'] for r in self.results.values()],
            'Precisão': [r['precision'] for r in self.results.values()],
            'Recall': [r['recall'] for r in self.results.values()],
            'F1-Score': [r['f1_score'] for r in self.results.values()],
            'CV Mean': [r['cv_mean'] for r in self.results.values()],
            'CV Std': [r['cv_std'] for r in self.results.values()]
        }).round(4)
        
        print("\n📈 MÉTRICAS GERAIS:")
        print(metrics_df.to_string(index=False))
        
        # Encontrar melhor modelo
        best_model_name = metrics_df.loc[metrics_df['F1-Score'].idxmax(), 'Modelo']
        best_f1 = metrics_df['F1-Score'].max()
        
        print(f"\n🏆 MELHOR MODELO: {best_model_name}")
        print(f"   F1-Score: {best_f1:.4f}")
        
        # Relatório detalhado do melhor modelo
        print(f"\n📋 RELATÓRIO DETALHADO - {best_model_name}:")
        best_results = self.results[best_model_name]
        print(classification_report(self.y_test, best_results['y_pred'], 
                                   target_names=['Nível 1', 'Nível 2', 'Nível 3', 'Nível 4']))
        
        # Salvar métricas
        metrics_df.to_csv('data/exports/model_performance_metrics.csv', index=False)
        print("💾 Métricas salvas em 'data/exports/model_performance_metrics.csv'")
        
        return best_model_name, metrics_df
    
    def analyze_tradeoffs(self):
        """Análise de trade-offs entre métricas"""
        print("\n" + "="*80)
        print("⚖️ ANÁLISE DE TRADE-OFFS")
        print("="*80)
        
        tradeoffs = []
        
        for name, results in self.results.items():
            precision = results['precision']
            recall = results['recall']
            f1 = results['f1_score']
            
            # Análise de sensibilidade
            if recall > 0.8:
                sensitivity = "🟢 Alta"
                sens_note = "Bom para detectar todos os alagamentos críticos"
            elif recall > 0.6:
                sensitivity = "🟡 Média"
                sens_note = "Equilibrio entre detecção e falsos positivos"
            else:
                sensitivity = "🔴 Baixa"
                sens_note = "Pode perder alagamentos importantes"
            
            # Análise de especificidade
            if precision > 0.8:
                specificity = "🟢 Alta"
                spec_note = "Poucos falsos alarmes"
            elif precision > 0.6:
                specificity = "🟡 Média"
                spec_note = "Alguns falsos alarmes aceitáveis"
            else:
                specificity = "🔴 Baixa"
                spec_note = "Muitos falsos alarmes"
            
            tradeoffs.append({
                'modelo': name,
                'sensibilidade': sensitivity,
                'especificidade': specificity,
                'recomendacao_uso': f"{sens_note}. {spec_note}",
                'cenario_ideal': self._get_ideal_scenario(precision, recall)
            })
        
        # Imprimir análise
        for trade in tradeoffs:
            print(f"\n🤖 {trade['modelo']}:")
            print(f"   Sensibilidade: {trade['sensibilidade']}")
            print(f"   Especificidade: {trade['especificidade']}")
            print(f"   💡 Recomendação: {trade['recomendacao_uso']}")
            print(f"   🎯 Cenário ideal: {trade['cenario_ideal']}")
    
    def _get_ideal_scenario(self, precision, recall):
        """Define cenário ideal baseado nas métricas"""
        if precision > 0.8 and recall > 0.8:
            return "Sistemas críticos de emergência"
        elif precision > recall:
            return "Sistemas com custo alto de falsos positivos"
        elif recall > precision:
            return "Sistemas onde é crítico não perder eventos"
        else:
            return "Sistemas com balanço entre custos"
    
    def feature_importance_analysis(self):
        """Análise de importância das features"""
        print("\n" + "="*80)
        print("📊 ANÁLISE DE IMPORTÂNCIA DAS FEATURES")
        print("="*80)
        
        # Análise para Random Forest
        if 'Random Forest' in self.results:
            rf_model = self.results['Random Forest']['model']
            feature_importance = pd.DataFrame({
                'feature': self.X.columns,
                'importance': rf_model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            print("\n🌲 Random Forest - Top 5 Features:")
            for idx, row in feature_importance.head().iterrows():
                print(f"   {row['feature']}: {row['importance']:.4f}")
        
        # Salvar importâncias
        if 'Random Forest' in self.results:
            feature_importance.to_csv('data/exports/feature_importance.csv', index=False)
            print("💾 Importância das features salva em 'data/exports/feature_importance.csv'")
    
    def run_complete_analysis(self):
        """Executa análise completa"""
        print("🚀 Iniciando Análise Completa de Machine Learning")
        print("="*60)
        
        # Criar diretório de exports se não existir
        import os
        os.makedirs('data/exports', exist_ok=True)
        
        # Executar pipeline
        self.initialize_models()
        self.train_and_evaluate()
        self.plot_confusion_matrices()
        self.plot_roc_curves()
        self.plot_precision_recall_curves()
        best_model, metrics = self.generate_performance_report()
        self.analyze_tradeoffs()
        self.feature_importance_analysis()
        
        print("\n" + "="*80)
        print("✅ ANÁLISE COMPLETA FINALIZADA")
        print("="*80)
        print(f"🏆 Melhor modelo identificado: {best_model}")
        print("📁 Todos os artefatos salvos em 'data/exports/'")
        print("📊 Gráficos: confusion_matrices.png, roc_curves.png, precision_recall_curves.png")
        print("📄 Dados: model_performance_metrics.csv, feature_importance.csv")
        
        return best_model, metrics

def main():
    """Função principal"""
    # Executar análise
    classifier = FloodSeverityClassifier('data/raw/data.csv')
    best_model, metrics = classifier.run_complete_analysis()
    
    print(f"\n🎯 Sistema pronto para produção com modelo: {best_model}")

if __name__ == "__main__":
    main()