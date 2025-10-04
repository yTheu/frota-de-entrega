from datetime import timedelta
from django.utils import timezone
from django.shortcuts import render,redirect, get_object_or_404
from django.contrib import messages
from .forms import VeiculoForm, MotoristaForm, EntregaForm, ManutencaoForm, AbastecimentoForm, CoordenadaForm
from .models import Veiculo, Motorista, Entrega, Manutencao, Abastecimento, Coordenada

# ------------------Sistema-------------------------------------------------------------------------

def index(request):
    return render(request,'index.html')

def coordenadasMapa(request):
    coordenadas = Coordenada.objects.all()
    return render(request, 'coordenadasMapa.html', {'coordenadas': coordenadas})

def listaVeiculos(request):
    veiculos = Veiculo.objects.all()
    return render(request, 'listaVeiculos.html', {'veiculos': veiculos})

def listaMotoristas(request):
    motoristas = Motorista.objects.all()
    return render(request, 'listaMotoristas.html', {'motoristas': motoristas})

def listaEntregas(request):
    entregas = Entrega.objects.all()
    return render(request, 'listaEntregas.html', {'entregas': entregas})
    
def listaManutencoes(request):
    manutencoes = get_object_or_404(id=id)
    return render(request, 'listaManutencoes.html', {'manutencoes': manutencoes})

# ----------------Motorista-------------------------------------
def cadastrarMotorista(request):
    if request.method == 'POST':
        form = MotoristaForm(request.POST)
        if form.is_valid():
            MotoristaForm.save()
            messages.success(request, 'Motorista cadastrado com sucesso')
            return redirect('listaMotoristas')
        else:
            messages.error(request, 'Erro ao cadastrar o motorista')
    else:
        form = MotoristaForm()

    return render(request, 'cadastrarMotorista.html', {'form': form})

def motoristasDisponiveis(request):
    if request.method ==' GET':
     motorista = Motorista.objects.get(disponivel=True)
     return render(request, 'motoristasDisponiveis.html', {'motorista': motorista})
     #return redirect('motoristasDisponiveis.html')
    else:
        messages.error(request, 'O motorista não está disponível')
        return redirect('index')
    
def abastecer(request):
    if request.method == 'POST':
        form = AbastecimentoForm(request.POST)
        if form.is_valid():
            AbastecimentoForm.save()
            messages.success(request, 'Abastecimento realizado com sucesso')
            return redirect('listaAbastecimentos')
        else:
            messages.error(request, 'Erro ao realizar o abastecimento')
    else:
        form = AbastecimentoForm()
    return render(request, 'abastecer.html', {'form': form})

# ----------------------Veiculo--------------------------------------------------
def cadastrarVeiculo(request):
    if request.method == 'POST':
        form = VeiculoForm(request.POST)
        if form.is_valid():
            VeiculoForm.save()
            messages.success(request, 'Veículo cadastrado com sucesso')
            return redirect('listaVeiculos')
        else:
            messages.error(request, 'Erro ao cadastrar o veículo')
    else:
        form = VeiculoForm()

    return render(request, 'cadastrarVeiculo.html', {'form': form})

def atualizarKm(request, id):
    veiculo = Veiculo.objects.get(id=id)
    if request.method == 'POST':
        form = VeiculoForm(request.POST, instance=veiculo)
        if form.is_valid():
            veiculo.km = request.POST.get('km')
            veiculo.save()
            messages.success(request, 'Quilometragem atualizada com sucesso')   
            return redirect('listaVeiculos')
        else:
            messages.error(request, 'Não foi possível atualizar a quilometragem')
    else:
        form = VeiculoForm(instance=veiculo)    
    return render(request, 'atualizarKm.html', {'veiculo': veiculo})

def veiculosDisponiveis(request):
    if request.method ==' GET':
     veiculo = Veiculo.objects.get(disponivel=True)
     return render(request, 'veiculosDisponiveis.html', {'veiculo': veiculo})
     #return redirect('veiculosDisponiveis.html')
    else:
        messages.error(request, 'O veículo não está disponível')
        return redirect('index')
# -------------------Manutenção--------------------------------------------
def realizarManutencao(request):
    if request.method == 'POST':
        form = ManutencaoForm(request.POST)
        if form.is_valid():
            manutencao = form.save(commit=False)
            ManutencaoForm.save()
            messages.success(request, 'Manutenção realizada com sucesso')
            return redirect('listaManutencoes')
        else:
            messages.error(request, 'Erro ao realizar a manutenção')
    else:
        form = ManutencaoForm()
    return render(request, 'realizarManutencao.html', {'form': form})

def proxManutencao(request, id):
    veiculo = get_object_or_404(Manutencao, id=id)
    return render(request, 'proxManutencao.html', {'veiculo': veiculo})
    


def verificarManutencoes(request):
    veiculo = get_object_or_404(Veiculo, id=id)
    if veiculo.precisa_manutencao():

        messages.warning(request, f' O veículo {veiculo.placa} precisa de manutenção!')
    else:
        messages.success(request, f'O veículo {veiculo.placa} está em boas condições.')

    return render(request, 'listaManutenções.html', {'veiculo': veiculo})


def agendarManutencao(request):
    if request.method == 'POST':
        form = ManutencaoForm(request.POST)
        if form.is_valid():
            manutencao = form.save(commit=False)
            manutencao.save()
            messages.success(request, 'Manutenção agendada com sucesso')
            return redirect('listaManutencoes')
        else:
            messages.error(request, 'Erro ao agendar a manutenção')
    else:
        form = ManutencaoForm()
    return render(request, 'agendarManutencao.html', {'form': form}) 

def alertaManutencao(request, id):
    veiculo = get_object_or_404(Veiculo, id=id)

    if veiculo.ultimaManutencao + timedelta(days=180) <= timezone.now().date():
        messages.warning(request, f' O veículo {veiculo.placa} precisa de manutenção!')   
        
    elif Manutencao.data - timedelta(days=7) <= timezone.now().date():
        messages.warning(request, f' O veículo {veiculo.placa} precisa de manutenção em breve!')
    else:
        messages.success(request, f' O veículo {veiculo.placa} está em boas condições.')
    return render(request, 'alertaManutenção.html', {'veiculo': veiculo})


#def solicitarManutencao(request): eu acho que n precisa pois a manutencao ja ta sendo solicitada no cadastrar manutencao com a função de agendar manutencao

# Entrega
def cadastrarEntrega(request):
    if request.method == 'POST':
        form = EntregaForm(request.POST)
        if form.is_valid():
            EntregaForm.save()
            messages.success(request, 'Entrega cadastrada com sucesso')
            return redirect('listaEntregas')
        else:
            messages.error(request, 'Erro ao cadastrar a entrega')
    else:
        form = EntregaForm()
    return render(request, 'cadastrarEntrega.html', {'form': form}) 

def iniciarEntrega(request, id):
    entrega = get_object_or_404(Entrega, id=id)
    if request.method == 'POST':
        entrega.status = 'EM ANDAMENTO'
        entrega.save()
        messages.success(request, 'Entrega iniciada com sucesso')
        return redirect('listaEntregas')
    else:
        messages.error(request, 'Não foi possível iniciar a entrega')
    return render(request, 'iniciarEntrega.html', {'entrega': entrega})

def monitorarEntrega(request, id):
    entrega = get_object_or_404(Entrega, id=id)
    return render(request, 'monitorarEntrega.html', {'entrega': entrega})

def atualizarStatus(request, id):
    entrega = get_object_or_404(Entrega, id=id)
    if request.method == 'POST':
        form = EntregaForm(request.POST, instance=entrega)
        if form.is_valid():
            entrega.status = request.POST.get('status')
            entrega.save()
            messages.success(request, 'Status da entrega atualizado com sucesso')   
            return redirect('listaEntregas')
        else:
            messages.error(request, 'Não foi possível atualizar o status da entrega')
    else:
        form = EntregaForm(instance=entrega)
    return render(request, 'detalhesEntregas.html', {'entrega': entrega})

def atualizarCoordenada(request):
    if request.method == 'POST':
        form = CoordenadaForm(request.POST)
        if form.is_valid():
            CoordenadaForm.save()
            messages.success(request, 'Coordenada atualizada com sucesso')
            return redirect('coordenadasMapa')
        else:
            messages.error(request, 'Erro ao atualizar a coordenada')
    else:
        form = CoordenadaForm()
    return render(request, 'atualizarCoordenada.html', {'form': form})
def concluirEntrega(request):
    if request.method == 'POST':
        entrega_id = request.POST.get('entrega_id')
        entrega = get_object_or_404(Entrega, id=entrega_id)
        entrega.status = 'CONCLUIDA'
        entrega.save()
        messages.success(request, 'Entrega concluída com sucesso')
        return redirect('listaEntregas')
    else:
        messages.error(request, 'Não foi possível concluir a entrega')
    return redirect('listaEntregas')
def alertaStatus(request): 
    entregas = get_object_or_404(id=id)
    if entregas.status == 'PENDENTE':
        messages.warning(request, 'Existem entregas pendentes!')
    elif entregas.status == 'EM TRANSITO':
        messages.info(request, 'Todas as entregas estão em andamento.')
    else:
        messages.success(request, 'as entregas foram concluídas.')
    return render(request, 'messagensAlertas.html', {'entregas': entregas})