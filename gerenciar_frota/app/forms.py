from django import forms
from .models import Veiculo, Motorista, Entrega, Manutencao, Abastecimento, Coordenada

class VeiculoForm(forms.ModelForm):
    class Meta:
        model = Veiculo
        fields = ['placa', 'modelo', 'km', 'autonomia', 'ultimaManutencao', 'disponivel']

class MotoristaForm(forms.ModelForm):
    class Meta:
        model = Motorista
        fields = ['cpf', 'nome', 'num_cnh', 'veiculoAtual', 'disponivel']

class EntregaForm(forms.ModelForm):
    class Meta:
        model = Entrega
        fields = ['origem', 'destino', 'status', 'veiculo']

class ManutencaoForm(forms.ModelForm):
    class Meta:
        model = Manutencao
        fields = ['veiculo', 'tipo', 'descricao', 'data', 'custo', 'status']

class AbastecimentoForm(forms.ModelForm):
    class Meta:
        model = Abastecimento
        fields = ['litros', 'custo', 'dataAbastecimento', 'veiculo']

class CoordenadaForm(forms.ModelForm):
    class Meta:
        model = Coordenada
        fields = ['latitude', 'longitude']

