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
    cep = forms.CharField(max_length=10, required=False, label="CEP")
    rua = forms.CharField(max_length=255, required=False, label="Rua")
    numero = forms.CharField(max_length=20, required=False, label="Número")
    bairro = forms.CharField(max_length=100, required=False, label="Bairro")
    cidade = forms.CharField(max_length=100, required=False, label="Cidade")
    estado = forms.CharField(max_length=50, required=False, label="Estado (UF)")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.error_messages = {'required': 'Este campo é obrigatório.'}

class VeiculoForm(forms.ModelForm):
    class Meta:
        model = Veiculo
        fields = ['placa', 'modelo', 'km', 'status', 'ultimaManutencao', 'km_ultima_manutencao', 'capacidade_kg']
        
        widgets = {
            'placa': forms.TextInput(attrs={'class': 'form-control'}),
            'modelo': forms.TextInput(attrs={'class': 'form-control'}),
            'km': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'ultimaManutencao': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'km_ultima_manutencao': forms.NumberInput(attrs={'class': 'form-control'}),
            'capacidade_kg': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
        
        labels = {
            'km': 'Quilometragem Atual',
            'ultimaManutencao': 'Data da Última Manutenção Preventiva',
            'km_ultima_manutencao': 'KM na Última Manutenção Preventiva',
            'capacidade_kg': 'Capacidade Máxima de Carga (Kg)',
        }

class MotoristaForm(forms.ModelForm):
    class Meta:
        model = PerfilMotorista
        fields = ['nome', 'cpf', 'num_cnh', 'disponivel']

LIMITE_MAXIMO_PESO_KG = 200.00
class EntregaForm(forms.ModelForm):
    # ver se o user quer usar o endereço cadastrado ou manual
    usar_endereco_cadastrado = forms.BooleanField(label="Usar meu endereço cadastrado como origem", required=False, initial=True, 
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    #origem 
    cep_origem = forms.CharField(label='CEP de Origem', max_length=9, required=False)
    estado_origem = forms.CharField(label='Estado', max_length=2, required=False)
    cidade_origem = forms.CharField(label='Cidade', required=False)
    bairro_origem = forms.CharField(label='Bairro', required=False)
    rua_origem = forms.CharField(label='Rua', required=False)
    numero_origem = forms.CharField(label='Nº', required=False)

    # destino
    cep_destino = forms.CharField(label='CEP de Destino', max_length=9, required=True)
    estado_destino = forms.CharField(label='Estado', max_length=2, required=True)
    cidade_destino = forms.CharField(label='Cidade', required=True)
    bairro_destino = forms.CharField(label='Bairro', required=True)
    rua_destino = forms.CharField(label='Rua', required=True)
    numero_destino = forms.CharField(label='Nº', required=True)

    class Meta:
        model = Entrega
        fields = [
            'nome_destinatario',
            'telefone_destinatario',
            'descricao_carga',
            'peso_kg',
            'fragil',
            'observacoes_entrega'
        ]
        widgets = {
            'peso_kg': forms.NumberInput(attrs={'max': str(LIMITE_MAXIMO_PESO_KG)}),
            'data_entrega_prevista': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'observacoes_entrega': forms.Textarea(attrs={'rows': 3}),
        }
        
    def __init__(self, *args, **kwargs):
        self.perfil_cliente = kwargs.pop('perfil_cliente', None)
        super().__init__(*args, **kwargs)
        
        if not (self.perfil_cliente and self.perfil_cliente.endereco):
            self.fields['usar_endereco_cadastrado'].initial = False
            self.fields['usar_endereco_cadastrado'].disabled = True
            for field_name in ['cep_origem', 'rua_origem', 'numero_origem', 'bairro_origem', 'cidade_origem', 'estado_origem']:
                 self.fields[field_name].required = True
        
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if isinstance(field.widget, forms.CheckboxInput):
                 field.widget.attrs['class'] = 'form-check-input'

    # validação do endereço (se vai usar o padrão do cadastro ou não)
    def clean(self):
        cleaned_data = super().clean()
        usar_cadastrado = cleaned_data.get('usar_endereco_cadastrado')

        if not usar_cadastrado:
            campos_origem = ['cep_origem', 'rua_origem', 'numero_origem', 'bairro_origem', 'cidade_origem', 'estado_origem']
            for campo in campos_origem:
                if not cleaned_data.get(campo):
                    self.add_error(campo, "Este campo é obrigatório se você não usar o endereço cadastrado.")
        
        return cleaned_data

    def clean_peso_kg(self):
        peso = self.cleaned_data.get('peso_kg')
     
        if peso is not None and peso > LIMITE_MAXIMO_PESO_KG:
            raise forms.ValidationError(
                f"O peso da carga não pode exceder {LIMITE_MAXIMO_PESO_KG:.0f} kg."
            )
            
        return peso
        
class ManutencaoForm(forms.ModelForm):
    class Meta:
        model = Manutencao
        fields = ['tipo', 'descricao', 'data', 'custo', 'status'] 
        
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'data': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'custo': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
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
        fields = [
            'nome_empresa', 
            'telefone',
            'cep',
            'rua',
            'numero',
            'bairro',
            'cidade',
            'estado',
        ]
    
        widgets = {
            'nome_empresa': forms.TextInput(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'cep': forms.TextInput(attrs={'class': 'form-control'}),
            'rua': forms.TextInput(attrs={'class': 'form-control'}),
            'numero': forms.TextInput(attrs={'class': 'form-control'}),
            'bairro': forms.TextInput(attrs={'class': 'form-control'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.TextInput(attrs={'class': 'form-control'}),
        }
