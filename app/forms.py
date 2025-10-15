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
    endereco_origem = forms.CharField(label='Endereço de Origem Completo', required=True)
    endereco_destino = forms.CharField(label='Endereço de Destino Completo', required=True)

    class Meta:
        model = Entrega
        fields = [
            'endereco_origem', 
            'endereco_destino',
            'nome_destinatario',
            'telefone_destinatario',
            'descricao_carga',
            'peso_kg',
            'volume_m3',
            'fragil',
            'data_entrega_prevista',
            'observacoes_entrega'
        ]
        widgets = {
            'data_entrega_prevista': forms.DateTimeInput(
                attrs={'type': 'datetime-local'}
            ),
            'observacoes_entrega': forms.Textarea(attrs={'rows': 3}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        
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
