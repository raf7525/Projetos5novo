"""
Formulários para o app Dashboard.
"""
from django import forms
from .models import RelatorioAlagamento

class RelatorioAlagamentoForm(forms.ModelForm):
    """
    Formulário para usuários criarem novos relatórios de alagamento.
    """
    class Meta:
        model = RelatorioAlagamento
        fields = [
            'latitude', 'longitude', 'bairro', 'endereco_aproximado',
            'nivel_severidade', 'descricao', 'altura_agua_cm', 'foto'
        ]
        widgets = {
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Latitude (Ex: -8.05428)'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Longitude (Ex: -34.8813)'}),
            'bairro': forms.Select(attrs={'class': 'form-select'}),
            'endereco_aproximado': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ponto de referência ou rua próxima'}),
            'nivel_severidade': forms.Select(attrs={'class': 'form-select'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Descreva a situação (opcional)'}),
            'altura_agua_cm': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Altura da água em cm (opcional)'}),
            'foto': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'latitude': 'Latitude',
            'longitude': 'Longitude',
            'bairro': 'Bairro Afetado',
            'endereco_aproximado': 'Endereço Aproximado',
            'nivel_severidade': 'Nível de Severidade',
            'descricao': 'Descrição Adicional',
            'altura_agua_cm': 'Altura da Água (cm)',
            'foto': 'Enviar Foto (Opcional)',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adicionar um botão ou funcionalidade JS para obter a localização
        self.fields['latitude'].help_text = 'Você pode obter as coordenadas clicando no mapa ou usando um botão.'
        self.fields['longitude'].help_text = 'As coordenadas serão preenchidas automaticamente.'

