from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from .models import Veiculo, PerfilMotorista, Entrega, Manutencao, Abastecimento, Coordenada, PerfilCliente

# -------------------------------
# LOGIN
# -------------------------------
class LoginForm(AuthenticationForm):
    """Formulário de login personalizado."""
    pass


# -------------------------------
# VEÍCULO
# -------------------------------
class VeiculoForm(forms.ModelForm):
    class Meta:
        model = Veiculo
        fields = ['placa', 'modelo', 'km', 'autonomia', 'ultimaManutencao', 'status']
        widgets = {
            'ultimaManutencao': forms.DateInput(attrs={'type': 'date'}),
        }


# -------------------------------
# MOTORISTA
# -------------------------------
class MotoristaForm(forms.ModelForm):
    class Meta:
        model = PerfilMotorista
        fields = ['nome', 'cpf', 'num_cnh', 'veiculoAtual', 'disponivel']


# -------------------------------
# ENTREGA
# -------------------------------
class EntregaForm(forms.ModelForm):
    class Meta:
        model = Entrega
        fields = ['origem', 'destino', 'data_inicio_prevista', 'data_fim_prevista']
        widgets = {
            'data_inicio_prevista': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'data_fim_prevista': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


# -------------------------------
# MANUTENÇÃO
# -------------------------------
class ManutencaoForm(forms.ModelForm):
    class Meta:
        model = Manutencao
        fields = ['veiculo', 'tipo', 'descricao', 'data', 'custo', 'status']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),
        }


# -------------------------------
# ABASTECIMENTO
# -------------------------------
class AbastecimentoForm(forms.ModelForm):
    class Meta:
        model = Abastecimento
        fields = ['litros', 'custo', 'dataAbastecimento', 'veiculo']
        widgets = {
            'dataAbastecimento': forms.DateInput(attrs={'type': 'date'}),
        }


# -------------------------------
# COORDENADAS
# -------------------------------
class CoordenadaForm(forms.ModelForm):
    class Meta:
        model = Coordenada
        fields = ['latitude', 'longitude']


# -------------------------------
# PERFIL CLIENTE
# -------------------------------
class PerfilClienteForm(forms.ModelForm):
    class Meta:
        model = PerfilCliente
        fields = ['nome_empresa', 'endereco', 'telefone']
