from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from .models import Veiculo, PerfilMotorista, Entrega, Manutencao, Abastecimento, Coordenada, PerfilCliente

class LoginForm(AuthenticationForm):
    #vou fazer manualmente
    pass

class VeiculoForm(forms.ModelForm):
    class Meta:
        model = Veiculo
        fields = ['placa', 'modelo', 'km', 'autonomia', 'ultimaManutencao', 'status']
        widgets = {
            'ultimaManutencao': forms.DateInput(attrs={'type': 'date'}),
        }

class MotoristaForm(forms.ModelForm):
    class Meta:
        model = PerfilMotorista
        fields = ['nome', 'cpf', 'num_cnh', 'disponivel']

class EntregaForm(forms.ModelForm):
    class Meta:
        model = Entrega
        fields = ['origem', 'destino']
        
class ManutencaoForm(forms.ModelForm):
    class Meta:
        model = Manutencao
        fields = ['veiculo', 'tipo', 'descricao', 'data', 'custo', 'status']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),
        }

class AbastecimentoForm(forms.ModelForm):
    class Meta:
        model = Abastecimento
        fields = ['litros', 'custo', 'dataAbastecimento', 'veiculo']
        widgets = {
            'dataAbastecimento': forms.DateInput(attrs={'type': 'date'}),
        }

class CoordenadaForm(forms.ModelForm):
    class Meta:
        model = Coordenada
        fields = ['latitude', 'longitude']

class PerfilClienteForm(forms.ModelForm):
    class Meta:
        model = PerfilCliente
        fields = ['nome_empresa', 'endereco', 'telefone']
