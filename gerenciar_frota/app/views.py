from datetime import timedelta
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, authenticate, logout # Importar funções de autenticação

from .forms import VeiculoForm, MotoristaForm, EntregaForm, ManutencaoForm, AbastecimentoForm, CoordenadaForm
from .models import Veiculo, PerfilMotorista, Entrega, Manutencao, Abastecimento, Coordenada, PerfilMotorista, PerfilCliente
from .forms import LoginForm # Vamos criar este formulário

# ------------------Sistema (Views Públicas ou Gerais)-------------------------------------------------------------------------

def index(request):
    """View da página inicial."""
    return render(request, 'index.html')

def test(request):
    """View de teste."""
    return render(request, 'teste.html')

def login_view(request):
    """View para o login personalizado."""
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # Redirecionar o usuário para o dashboard apropriado
                return redirect('dashboard') # Redireciona para uma view que decide o dashboard
            else:
                messages.error(request, 'Nome de usuário ou senha inválidos.')
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})

@login_required # Garante que o usuário esteja logado para acessar
def logout_view(request):
    """View para fazer logout."""
    logout(request)
    messages.success(request, 'Você foi desconectado com sucesso.')
    return redirect('index') # Redireciona para a página inicial após o logout

@login_required
def dashboard(request):
    """
    View que redireciona o usuário para o dashboard apropriado
    com base no seu tipo (Administrador, PerfilMotorista, Cliente).
    """
    user = request.user
    if user.is_staff: # assumes admin users are staff
        return redirect('dashboard_admin')
    try:
        motorista_profile = user.perfilmotorista
        return redirect('dashboard_motorista')
    except PerfilMotorista.DoesNotExist:
        pass # User is not a PerfilMotorista, check for Cliente

    try:
        cliente_profile = user.perfilcliente
        return redirect('dashboard_cliente')
    except PerfilCliente.DoesNotExist:
        pass # User is not a Cliente

    # If somehow a logged in user is neither staff, PerfilMotorista, nor Cliente
    messages.warning(request, 'Seu tipo de usuário não foi reconhecido. Entre em contato com o administrador.')
    logout(request) # Optional: log out unrecognized users
    return redirect('index')

# ------------------Views do Administrador-------------------------------------------------------------------------

# Helper function to check if user is admin (staff)
def is_admin(user):
    return user.is_staff

@login_required
@user_passes_test(is_admin) # Garante que apenas administradores acessem
def dashboard_admin(request):
    """Dashboard do Administrador."""
    # Lógica para exibir informações relevantes para o administrador
    total_veiculos = Veiculo.objects.count()
    total_motoristas = PerfilMotorista.objects.count()
    total_entregas_pendentes = Entrega.objects.filter(status='PENDENTE').count()
    # Adicione outras informações relevantes aqui
    return render(request, 'ADMIN/dashboard_admin.html', {
        'total_veiculos': total_veiculos,
        'total_motoristas': total_motoristas,
        'total_entregas_pendentes': total_entregas_pendentes,
    })

@login_required
@user_passes_test(is_admin)
def lista_veiculos(request):
    """Lista todos os veículos (acesso apenas para admin)."""
    veiculos = Veiculo.objects.all()
    return render(request, 'VEICULOS/listaVeiculos.html', {'veiculos': veiculos})

@login_required
@user_passes_test(is_admin)
def adicionar_veiculo(request):
    """Adicionar novo veículo (acesso apenas para admin)."""
    if request.method == 'POST':
        form = VeiculoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Veículo adicionado com sucesso!')
            return redirect('lista_veiculos')
    else:
        form = VeiculoForm()
    return render(request, 'VEICULOS/adicionarVeiculo.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def editar_veiculo(request, pk):
    """Editar veículo existente (acesso apenas para admin)."""
    veiculo = get_object_or_404(Veiculo, pk=pk)
    if request.method == 'POST':
        form = VeiculoForm(request.POST, instance=veiculo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Veículo atualizado com sucesso!')
            return redirect('lista_veiculos')
    else:
        form = VeiculoForm(instance=veiculo)
    return render(request, 'VEICULOS/editarVeiculo.html', {'form': form, 'veiculo': veiculo})

@login_required
@user_passes_test(is_admin)
def deletar_veiculo(request, pk):
    """Deletar veículo (acesso apenas para admin)."""
    veiculo = get_object_or_404(Veiculo, pk=pk)
    if request.method == 'POST':
        veiculo.delete()
        messages.success(request, 'Veículo excluído com sucesso!')
        return redirect('lista_veiculos')
    return render(request, 'VEICULOS/confirmarDeletarVeiculo.html', {'veiculo': veiculo})


# ... outras views de gerenciamento (Motoristas, Entregas, Manutenções, Abastecimentos) para Admin
# que também devem usar @login_required e @user_passes_test(is_admin)

@login_required
@user_passes_test(is_admin)
def lista_motoristas(request):
     """Lista todos os motoristas (acesso apenas para admin)."""
     motoristas = PerfilMotorista.objects.all()
     return render(request, 'MOTORISTAS/listaMotoristas.html', {'motoristas': motoristas})

# Adicionar, editar e deletar motorista views (apenas para admin)
# ...

@login_required
@user_passes_test(is_admin)
def lista_entregas(request):
     """Lista todas as entregas (acesso apenas para admin)."""
     entregas = Entrega.objects.all()
     return render(request, 'ENTREGAS/listaEntregas.html', {'entregas': entregas})

# Adicionar, editar e deletar entrega views (apenas para admin)
# ... cadastrarEntregas, editarEntrega, deletarEntrega - certifique-se de usar os decorators de permissão

@login_required
@user_passes_test(is_admin)
def lista_manutencoes(request):
    """Lista todas as manutenções (acesso apenas para admin)."""
    manutencoes = Manutencao.objects.all()
    return render(request, 'MANUTENCAO/listaManutencoes.html', {'manutencoes': manutencoes})

# Adicionar, editar e deletar manutencao views (apenas para admin)
# ...

@login_required
@user_passes_test(is_admin)
def alerta_manutencao(request):
    """Alertas de manutenção (acesso apenas para admin)."""
    # Sua lógica de alerta de manutenção aqui
    threshold_km = 10000 # Exemplo: alerta se a última manutenção foi há mais de 10000 km
    threshold_dias = 180 # Exemplo: alerta se a última manutenção foi há mais de 180 dias

    veiculos_alerta_km = Veiculo.objects.filter(km__gte=models.F('ultimaManutencao_km') + threshold_km)
    veiculos_alerta_dias = Veiculo.objects.filter(ultimaManutencao__lte=timezone.now() - timedelta(days=threshold_dias))

    veiculos_alerta = (veiculos_alerta_km | veiculos_alerta_dias).distinct() # Combine e remova duplicados

    return render(request, 'MANUTENCAO/alertaManutencao.html', {'veiculos_alerta': veiculos_alerta})

@login_required
@user_passes_test(is_admin)
def alerta_status(request):
    """Alertas de status de entrega (acesso apenas para admin)."""
    # Lógica para alertas de status de entrega
    # Exemplo: Entregas pendentes há muito tempo, entregas atrasadas, etc.
    entregas_atrasadas = Entrega.objects.filter(
        data_fim_prevista__lt=timezone.now(),
        status__in=['PENDENTE', 'EM_ROTA'] # Ou outros status que indiquem não entregue
    )
    return render(request, 'ENTREGAS/alertaStatus.html', {'entregas_atrasadas': entregas_atrasadas})


@login_required
@user_passes_test(is_admin)
def coordenadasMapa(request):
    """Mapa de coordenadas (acesso apenas para admin)."""
    coordenadas = Coordenada.objects.all()
    return render(request, 'ENTREGAS/coordenadasMapa.html', {'coordenadas': coordenadas})


# ------------------Views do PerfilMotorista-------------------------------------------------------------------------

# Helper function to check if user is a PerfilMotorista
def is_motorista(user):
    try:
        user.perfilmotorista
        return True
    except PerfilMotorista.DoesNotExist:
        return False

@login_required
@user_passes_test(is_motorista) # Garante que apenas motoristas acessem
def dashboard_motorista(request):
    """Dashboard do PerfilMotorista."""
    motorista_perfil = request.user.perfilmotorista
    # Obter as entregas atribuídas a este motorista
    entregas_atribuidas = Entrega.objects.filter(motorista=motorista_perfil) # Você precisará associar Entrega a PerfilMotorista/PerfilMotorista

    # Lógica para exibir informações relevantes para o motorista
    return render(request, 'MOTORISTA/dashboard_motorista.html', {
        'motorista': motorista_perfil,
        'entregas_atribuidas': entregas_atribuidas,
    })

@login_required
@user_passes_test(is_motorista)
def registrar_abastecimento(request):
    """Registrar novo abastecimento (acesso apenas para motorista)."""
    if request.method == 'POST':
        form = AbastecimentoForm(request.POST)
        if form.is_valid():
            abastecimento = form.save(commit=False)
            # Associe o abastecimento ao motorista logado e ao veículo atual do motorista
            motorista_perfil = request.user.perfilmotorista
            abastecimento.motorista = motorista_perfil
            abastecimento.veiculo = motorista_perfil.veiculoAtual # Você precisará de um campo veiculoAtual no PerfilMotorista
            abastecimento.save()
            messages.success(request, 'Abastecimento registrado com sucesso!')
            return redirect('dashboard_motorista') # Redireciona para o dashboard do motorista
    else:
        form = AbastecimentoForm()
    return render(request, 'ABASTECIMENTO/registrarAbastecimento.html', {'form': form})


@login_required
@user_passes_test(is_motorista)
def solicitar_manutencao(request):
    """Solicitar manutenção (acesso apenas para motorista)."""
    if request.method == 'POST':
        form = ManutencaoForm(request.POST) # Você pode precisar de um formulário simplificado para o motorista
        if form.is_valid():
            solicitacao = form.save(commit=False)
            # Associe a solicitação ao motorista logado e ao veículo atual
            motorista_perfil = request.user.perfilmotorista
            solicitacao.motorista = motorista_perfil
            solicitacao.veiculo = motorista_perfil.veiculoAtual # Você precisará de um campo veiculoAtual no PerfilMotorista
            solicitacao.status = 'SOLICITADA' # Defina um status inicial
            solicitacao.save()
            messages.success(request, 'Solicitação de manutenção enviada com sucesso!')
            return redirect('dashboard_motorista')
    else:
        form = ManutencaoForm() # Use o formulário de manutenção ou um formulário simplificado
    return render(request, 'MANUTENCAO/solicitarManutencao.html', {'form': form})

# View para o motorista ver suas entregas
@login_required
@user_passes_test(is_motorista)
def minhas_entregas(request):
    motorista_perfil = request.user.perfilmotorista
    entregas = Entrega.objects.filter(motorista=motorista_perfil) # Filtra as entregas pelo motorista logado
    return render(request, 'MOTORISTA/minhasEntregas.html', {'entregas': entregas})

# View para o motorista atualizar o status de uma entrega específica
@login_required
@user_passes_test(is_motorista)
def atualizar_status_entrega(request, pk):
    entrega = get_object_or_404(Entrega, pk=pk)
    # Garante que o motorista logado é o responsável por esta entrega
    if entrega.motorista != request.user.perfilmotorista:
        messages.error(request, 'Você não tem permissão para atualizar esta entrega.')
        return redirect('minhas_entregas')

    # Você precisará de um formulário simples para atualizar o status da entrega
    # Ou pode fazer isso diretamente com botões na página de detalhes da entrega
    # Exemplo simples (pode ser melhorado com um formulário):
    if request.method == 'POST':
        novo_status = request.POST.get('status') # Assume que você envia o novo status via POST
        if novo_status in ['EM_ROTA', 'ENTREGUE', 'PROBLEMA']: # Valide os status permitidos
            entrega.status = novo_status
            # Atualizar a data_inicio_real ou data_fim_real dependendo do status
            if novo_status == 'EM_ROTA' and not entrega.data_inicio_real:
                 entrega.data_inicio_real = timezone.now()
            if novo_status == 'ENTREGUE' and not entrega.data_fim_real:
                 entrega.data_fim_real = timezone.now()

            entrega.save()
            messages.success(request, f'Status da entrega {entrega.id} atualizado para {novo_status}.')
            return redirect('minhas_entregas') # Ou redireciona para a página de detalhes da entrega

    return render(request, 'MOTORISTA/atualizarStatusEntrega.html', {'entrega': entrega}) # Template para o formulário ou botões de status


# ------------------Views do Cliente-------------------------------------------------------------------------

# Helper function to check if user is a Cliente
def is_cliente(user):
    try:
        user.perfilcliente
        return True
    except PerfilCliente.DoesNotExist:
        return False

@login_required
@user_passes_test(is_cliente) # Garante que apenas clientes acessem
def dashboard_cliente(request):
    """Dashboard do Cliente."""
    cliente_perfil = request.user.perfilcliente
    # Obter as entregas cadastradas por este cliente
    entregas_cadastradas = Entrega.objects.filter(cliente=cliente_perfil) # Você precisará associar Entrega a PerfilCliente

    # Lógica para exibir informações relevantes para o cliente
    return render(request, 'CLIENTE/dashboard_cliente.html', {
        'cliente': cliente_perfil,
        'entregas_cadastradas': entregas_cadastradas,
    })

@login_required
@user_passes_test(is_cliente)
def cadastrar_pedido(request):
    """Cliente cadastra um novo pedido/entrega."""
    if request.method == 'POST':
        form = EntregaForm(request.POST) # Pode precisar de um formulário simplificado para o cliente
        if form.is_valid():
            entrega = form.save(commit=False)
            # Associe a entrega ao cliente logado
            entrega.cliente = request.user.perfilcliente
            entrega.status = 'PENDENTE' # Status inicial da entrega
            entrega.save()
            messages.success(request, 'Pedido cadastrado com sucesso! Aguardando alocação.')
            return redirect('dashboard_cliente') # Redireciona para o dashboard do cliente
    else:
        form = EntregaForm() # Use o formulário de entrega ou um formulário simplificado para o cliente
    return render(request, 'CLIENTE/cadastrarPedido.html', {'form': form})

@login_required
@user_passes_test(is_cliente)
def meus_pedidos(request):
    """Cliente visualiza seus pedidos cadastrados."""
    cliente_perfil = request.user.perfilcliente
    pedidos = Entrega.objects.filter(cliente=cliente_perfil)
    return render(request, 'CLIENTE/meusPedidos.html', {'pedidos': pedidos})

# View para o cliente ver o status de um pedido específico
@login_required
@user_passes_test(is_cliente)
def status_pedido(request, pk):
    pedido = get_object_or_404(Entrega, pk=pk)
    # Garante que o cliente logado é o dono deste pedido
    if pedido.cliente != request.user.perfilcliente:
        messages.error(request, 'Você não tem permissão para visualizar este pedido.')
        return redirect('meus_pedidos')

    return render(request, 'CLIENTE/statusPedido.html', {'pedido': pedido})


# Você precisará criar o LoginForm em app/forms.py
# E os templates para os dashboards e as novas funcionalidades
