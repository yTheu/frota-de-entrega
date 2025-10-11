from django import forms
from .models import Veiculo, Motorista, Entrega, Manutencao, Abastecimento, Coordenada

class VeiculoForm(forms.ModelForm):
    class Meta:
        model = Veiculo
        fields = ['placa', 'modelo','km', 'autonomia', 'ultimaManutencao', 'status']

class MotoristaForm(forms.ModelForm):
    class Meta:
        model = Motorista
        fields = ['cpf', 'nome', 'num_cnh', 'veiculoAtual', 'disponivel']

class EntregaForm(forms.ModelForm):
    class Meta:
        model = Entrega
        fields = ['origem', 'destino', 'status', 'veiculo', 'data_inicio_prevista', 'data_fim_prevista']

    #mostrar só os veículos disponíveis
    def __init__(self, *args, **kwargs):
            super(EntregaForm, self).__init__(*args, **kwargs)
            self.fields['veiculo'].queryset = Veiculo.objects.filter(status='DISPONIVEL')

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
