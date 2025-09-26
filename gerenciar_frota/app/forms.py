from django import forms
from .models import Veiculo, Motorista

class VeiculoForm(forms.ModelForm):
    class Meta:
        model = Veiculo
        fields = ['placa', 'modelo', 'km', 'autonomia', 'ultimaManutencao']

class MotoristaForm(forms.ModelForm):
    class Meta:
        model = Motorista
        fields = ['cpf', 'nome', 'num_cnh', 'veiculoAtual']

class EntregaForm(forms.ModelForm):
    class Meta:
        model = Entrega
        fields = ['origem', 'destino', 'status', 'veiculo']

class ManutencaoForm(forms.ModelForm):
    class Meta:
        model = Manutencao
        fields = ['veiculo', 'tipo', 'descricao', 'data', 'custo']
