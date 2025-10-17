from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from .models import Veiculo, PerfilMotorista, Entrega, Manutencao, Abastecimento, Coordenada, PerfilCliente

class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['username'].widget = forms.TextInput(attrs={
            'class': 'form-control form-control-lg', 
            'placeholder': 'Nome de usuário',
            'autofocus': True
        })
        self.fields['password'].widget = forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Senha'
        })

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
    #origem 
    cep_origem = forms.CharField(label='CEP de Origem', max_length=9)
    estado_origem = forms.CharField(label='Estado de Origem', max_length=2)
    cidade_origem = forms.CharField(label='Cidade de Origem')
    bairro_origem = forms.CharField(label='Bairro de Origem')
    rua_origem = forms.CharField(label='Rua de Origem')
    numero_origem = forms.CharField(label='Nº de Origem')

    # destino
    cep_destino = forms.CharField(label='CEP de Destino', max_length=9)
    estado_destino = forms.CharField(label='Estado de Destino', max_length=2)
    cidade_destino = forms.CharField(label='Cidade de Destino')
    bairro_destino = forms.CharField(label='Bairro de Destino')
    rua_destino = forms.CharField(label='Rua de Destino')
    numero_destino = forms.CharField(label='Nº de Destino')

    class Meta:
        model = Entrega
        fields = [
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
            'data_entrega_prevista': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
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
