from django.shortcuts import render
from django.contrib import messages
from .forms import VeiculoForm, MotoristaForm, EntregaForm, ManutencaoForm

# Sistema
def cadastrarVeiculo(request):
    if request.method == 'POST':
        form = VeiculoForm(request.POST)
        if form.is_valid():
            veiculo.save()
            messages.success(request, 'Veículo cadastrado com sucesso')
            return redirect('listaVeiculos')
        else:
            messages.error(request, 'Erro ao cadastrar o veículo')
    else:
        form = VeiculoForm()

    return render(request, 'cadastrarVeiculo.html', {'form': form})

def cadastrarMotorista():
    if request.method == 'POST':
        form = MotoristaForm(request.POST)
        if form.is_valid():
            motorista.save()
            messages.success(resquest, 'Motorista cadastrado com sucesso')
            return redirect('listaMotoristas')
        else:
            messages.error(request, 'Erro ao cadastrar o motorista')
    else:
        form = MotoristaForm()

    return render(request, 'cadastrarMotorista.html', {'form': form})

def cadastrarEntrega():
    if request.method == 'POST':
        form = EntregaForm(request.POST)
        if form.is_valid():
            entrega.save()
            messages.success(reques, 'Entrega cadastrada com sucesso')
            return redirect('listaEntregas')
        else:
            messages.error(request, 'Erro ao cadastrar a entrega')
    else:
        form = EntregaForm()
    return render(request, 'cadastrarEntrega.html', {'form': form})

def veiculosDisponiveis():
def motoristasDisponiveis():

# Veiculo
def atualizarKm():

# Manutenção
def realizarManutencao():
def proxManutencao():
def verificarManutencoes():
def agendarManutencao():
def alertaManutencao():

# Motorista
def abastecer():
def solicitarManutencao():

# Entrega
def iniciarEntrega():
def monitorarEntrega():
def atualizarStatus():
def atualizarCoordenada():
def concluirEntrega():
def alertaStatus():
