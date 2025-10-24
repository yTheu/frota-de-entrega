from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
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


class ClienteRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, required=False, label="Nome")
    last_name = forms.CharField(max_length=150, required=False, label="Sobrenome")
    email = forms.EmailField(required=True, label="E-mail")
    
    nome_empresa = forms.CharField(max_length=100, required=False, label="Nome da Empresa")
    endereco = forms.CharField(max_length=255, required=False, label="Endereço Principal")
    telefone = forms.CharField(max_length=20, required=False, label="Telefone de Contato")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

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

LIMITE_MAXIMO_PESO_KG = 1000.00
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
            'observacoes_entrega'
        ]
        widgets = {
            'peso_kg': forms.NumberInput(attrs={'max': str(LIMITE_MAXIMO_PESO_KG)}),
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
        fields = ['tipo', 'descricao', 'data']
        
        widgets = {
            'tipo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descreva o problema em detalhes. Ex: Barulho estranho no motor ao acelerar.'
            }),
            'data': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }
        
        labels = {
            'tipo': 'Tipo de Manutenção',
            'descricao': 'Descrição do Problema',
            'data': 'Data da Ocorrência',
        }

class AbastecimentoForm(forms.ModelForm):
    class Meta:
        model = Abastecimento
        fields = ['litros', 'custo', 'dataAbastecimento']
        
        widgets = {
            'litros': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01',
                'placeholder': 'Ex: 50.25'
            }),
            'custo': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01',
                'placeholder': 'Ex: 250.00'
            }),
            'dataAbastecimento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }
 
        labels = {
            'litros': 'Quantidade (Litros)',
            'custo': 'Custo Total (R$)',
            'dataAbastecimento': 'Data do Abastecimento',
        }

class CoordenadaForm(forms.ModelForm):
    class Meta:
        model = Coordenada
        fields = ['latitude', 'longitude']

class PerfilClienteForm(forms.ModelForm):
    class Meta:
        model = PerfilCliente
        fields = ['nome_empresa', 'endereco', 'telefone']
