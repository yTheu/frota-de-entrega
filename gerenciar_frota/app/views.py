from datetime import timedelta
from django.utils import timezone
from django.shortcuts import render,redirect, get_object_or_404
from django.contrib import messages
from .forms import VeiculoForm, MotoristaForm, EntregaForm, ManutencaoForm, AbastecimentoForm, CoordenadaForm
from .models import Veiculo, Motorista, Entrega, Manutencao, Abastecimento, Coordenada

# ------------------Sistema-------------------------------------------------------------------------
def det(request, id):
    veiculo = get_object_or_404(Veiculo, id=id)
    return render(request,'VEICULOS/listadetalhes.html',{'veiculo': veiculo})
 
def index(request):
    return render(request,'index.html')

def test(request):
    return render(request,'teste.html')

def coordenadasMapa(request):
    coordenadas = Coordenada.objects.all()
    return render(request, 'ENTREGAS/coordenadasMapa.html', {'coordenadas': coordenadas})

def listaVeiculos(request):
    veiculos = Veiculo.objects.all()
    return render(request, 'VEICULOS/listaVeiculos.html', {'veiculos': veiculos})

def listaMotoristas(request):
    motoristas = Motorista.objects.all()
    return render(request, 'MOTORISTAS/listaMotoristas.html', {'motoristas': motoristas})

def listaEntregas(request):
    entregas = Entrega.objects.all()
    return render(request, 'ENTREGAS/listaEntregas.html', {'entregas': entregas})
    
def listaManutencoes(request):
    manutencoes = Manutencao.objects.all()
    return render(request, 'MANUTENÇÃO/listaManutencoes.html', {'manutencoes': manutencoes})

# ----------------Motorista-------------------------------------
def cadastrarMotorista(request):
    if request.method == 'POST':
        form = MotoristaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Motorista cadastrado com sucesso')
            return redirect('lista_motoristas')
        else:
            messages.error(request, 'Erro ao cadastrar o motorista')
    else:
        form = MotoristaForm()

    return render(request, 'MOTORISTAS/cadastrarMotorista.html', {'form': form})

def motoristasDisponiveis(request):
    if request.method ==' GET':
        motoristas_disponiveis = Motorista.objects.filter(disponivel=True)
        return render(request, 'MOTORISTAS/motoristasDisponiveis.html', {'motoristas': motoristas_disponiveis})

    else:
        messages.error(request, 'O motorista não está disponível')
        return redirect('index')
    
def abastecer(request):
    if request.method == 'POST':
        form = AbastecimentoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Abastecimento realizado com sucesso')
            return redirect('index')
        else:
            messages.error(request, 'Erro ao realizar o abastecimento')
    else:
        form = AbastecimentoForm()
    return render(request, 'MOTORISTAS/abastecer.html', {'form': form})

# ----------------------Veiculo--------------------------------------------------
def cadastrarVeiculo(request):
    if request.method == 'POST':
        form = VeiculoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Veículo cadastrado com sucesso')
            return redirect('lista_veiculos')
        else:
            messages.error(request, 'Erro ao cadastrar o veículo')
    else:
        form = VeiculoForm()

    return render(request, 'VEICULOS/cadastrarVeiculos.html', {'form': form})

def atualizarKm(request, id):
    veiculo = Veiculo.objects.get(id=id)
    if request.method == 'POST':
        form = VeiculoForm(request.POST, instance=veiculo)
        if form.is_valid():
            veiculo.km = request.POST.get('km')
            veiculo.save()
            messages.success(request, 'Quilometragem atualizada com sucesso')   
            return redirect('lista_veiculos')
        else:
            messages.error(request, 'Não foi possível atualizar a quilometragem')
    else:
        form = VeiculoForm(instance=veiculo)    
    return render(request, 'VEICULOS/atualizarKm.html', {'veiculo': veiculo})

def veiculosDisponiveis(request):
    if request.method == 'GET':
     veiculos = Veiculo.objects.filter(status='DISPONIVEL')
     return render(request, 'VEICULOS/veiculosDisponiveis.html', {'veiculos': veiculos})
    else:
        messages.error(request, 'O veículo não está disponível')
        return redirect('index')
    

# -------------------Manutenção--------------------------------------------
def alertaManutencao(request):
    veiculos_manutencao = []
    for veiculo in Veiculo.objects.all():
        if veiculo.precisa_manutencao():
            veiculos_manutencao.append(veiculo)
    return render(request, 'MANUTENÇÃO/alertaManutencao.html', {'veiculos': veiculos_manutencao})

def realizarManutencao(request):
    if request.method == 'POST':
        form = ManutencaoForm(request.POST)
        if form.is_valid():
            manutencao = form.save()
            veiculo = manutencao.veiculo
            veiculo.status = 'EM_MANUTENCAO'
            veiculo.save()
            messages.success(request, 'Manutenção realizada com sucesso')
            return redirect('lista_manutencoes')
        else:
            messages.error(request, 'Erro ao realizar a manutenção')
    else:
        form = ManutencaoForm()
    return render(request, 'MANUTENÇÃO/realizarManutencao.html', {'form': form})

def proxManutencao(request, id):
    veiculo = get_object_or_404(Manutencao, id=id)
    return render(request, 'MANUTENÇÃO/proximaManutencao.html', {'veiculo': veiculo})

def verificarManutencoes(request, id):
    veiculo = get_object_or_404(Veiculo, id=id)
    if veiculo.precisa_manutencao():

        messages.warning(request, f' O veículo {veiculo.placa} precisa de manutenção!')
    else:
        messages.success(request, f'O veículo {veiculo.placa} está em boas condições.')

    return render(request, 'MANUTENÇÃO/listaManutencoes.html', {'veiculo': veiculo})


def agendarManutencao(request):
    if request.method == 'POST':
        form = ManutencaoForm(request.POST)
        if form.is_valid():
            manutencao = form.save()
            veiculo = manutencao.veiculo
            veiculo.status = 'EM_MANUTENCAO'
            veiculo.save()
            messages.success(request, 'Manutenção agendada com sucesso')
            return redirect('lista_manutencoes')
        else:
            messages.error(request, 'Erro ao agendar a manutenção')
    else:
        form = ManutencaoForm()
    return render(request, 'MANUTENÇÃO/agendarManutencao.html', {'form': form}) 

# Entrega
def cadastrarEntrega(request):
    if request.method == 'POST':
        form = EntregaForm(request.POST)
        if form.is_valid():
            entrega = form.save(commit=False)
            entrega.save()
            veiculo = entrega.veiculo
            veiculo.status = 'EM_ENTREGA'
            veiculo.save()
            messages.success(request, f'Entrega para o veículo {veiculo.placa} cadastrada com sucesso!')
            return redirect('lista_entregas')
        else:
            messages.error(request, 'Erro ao cadastrar a entrega')
    else:
        form = EntregaForm()
    return render(request, 'ENTREGAS/cadastrarEntregas.html', {'form': form})

def iniciarEntrega(request, id):
    entrega = get_object_or_404(Entrega, id=id)
    if request.method == 'POST':
        entrega.status = 'EM_TRANSITO'
        entrega.save()
        messages.success(request, 'Entrega iniciada com sucesso')
        return redirect('lista_entregas')
    else:
        messages.error(request, 'Não foi possível iniciar a entrega')
    return render(request, 'ENTREGAS/detalhesEntregas.html', {'entrega': entrega})

def monitorarEntrega(request, id):
    entrega = get_object_or_404(Entrega, id=id)
    return render(request, 'ENTREGAS/localizaçãoEntregas.html', {'entrega': entrega})

def atualizarStatus(request, id):
    entrega = get_object_or_404(Entrega, id=id)
    if request.method == 'POST':
        form = EntregaForm(request.POST, instance=entrega)
        if form.is_valid():
            entrega.status = request.POST.get('status')
            entrega.save()
            messages.success(request, 'Status da entrega atualizado com sucesso')   
            return redirect('lista_entregas')
        else:
            messages.error(request, 'Não foi possível atualizar o status da entrega')
    else:
        form = EntregaForm(instance=entrega)
    return render(request, 'ENTREGAS/detalhesEntregas.html', {'entrega': entrega})

def atualizarCoordenada(request):
    if request.method == 'POST':
        form = CoordenadaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Coordenada atualizada com sucesso')
            return redirect('mapa_coordenadas')
        else:
            messages.error(request, 'Erro ao atualizar a coordenada')
    else:
        form = CoordenadaForm()
    return render(request, 'ENTREGAS/atualizarCoordenadas.html', {'form': form})

def concluirEntrega(request):
    if request.method == 'POST':
        entrega_id = request.POST.get('entrega_id')
        entrega = get_object_or_404(Entrega, id=entrega_id)
        entrega.status = 'CONCLUIDA'
        entrega.save()
        veiculo = entrega.veiculo
        veiculo.status = 'DISPONIVEL'
        veiculo.save()
        messages.success(request, 'Entrega concluída com sucesso')
        return redirect('lista_entregas')
    else:
        messages.error(request, 'Não foi possível concluir a entrega')
    return redirect('lista_entregas')

def alertaStatus(request): 
    entregas = Entrega.objects.exclude(status='CONCLUIDA')
    if not entregas.exists():
        messages.success(request, 'Todas as entregas foram concluídas.')
    return render(request, 'ENTREGAS/mensagensAlertas.html', {'entregas': entregas})
