from datetime import timedelta
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, authenticate, logout
from django.db import models, transaction
from django.core.paginator import Paginator
from django.db.models import Q
from .forms import VeiculoForm, MotoristaForm, EntregaForm, ManutencaoForm, AbastecimentoForm, CoordenadaForm
from .models import Veiculo, PerfilMotorista, Entrega, Manutencao, Abastecimento, Coordenada, PerfilMotorista, PerfilCliente
from .forms import LoginForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group

# ------------------Sistema (Views Públicas ou Gerais)-------------------------------------------------------------------------

#dps desse projeto, quero distância desse vscode 

def index(request):
    return render(request, 'index.html')

def test(request):
    return render(request, 'teste.html')

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard') 
            else:
                messages.error(request, 'Nome de usuário ou senha inválidos.')
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Você foi desconectado com sucesso.')
    return redirect('index')

@login_required
def dashboard(request):
    user = request.user
    if user.is_staff:
        return redirect('dashboard_admin')
    try:
        motorista_profile = user.perfilmotorista
        return redirect('dashboard_motorista')
    except PerfilMotorista.DoesNotExist:
        pass

    try:
        cliente_profile = user.perfilcliente
        return redirect('dashboard_cliente')
    except PerfilCliente.DoesNotExist:
        pass

    messages.warning(request, 'Seu tipo de usuário não foi reconhecido. Entre em contato com o administrador.')
    logout(request)
    return redirect('index')

# ------------------Views do Administrador-------------------------------------------------------------------------
def is_admin(user):
    return user.is_staff

@login_required
@user_passes_test(is_admin) #apenas adms tem acesso
def dashboard_admin(request):
    total_veiculos = Veiculo.objects.count()
    total_motoristas = PerfilMotorista.objects.count()
    total_entregas_pendentes = Entrega.objects.filter(status='PENDENTE').count()
    return render(request, 'ADMIN/dashboard_admin.html', {
        'total_veiculos': total_veiculos,
        'total_motoristas': total_motoristas,
        'total_entregas_pendentes': total_entregas_pendentes,
    })

@login_required
@user_passes_test(is_admin)
def lista_veiculos(request):
    qs = Veiculo.objects.all()

    #filtrar
    q = request.GET.get('q', '').strip()
    status = request.GET.get('status', '')
    min_km = request.GET.get('min_km', '')
    max_km = request.GET.get('max_km', '')
    order = request.GET.get('order', 'modelo')

    if q:
        qs = qs.filter(Q(modelo__icontains=q) | Q(placa__icontains=q))
    if status:
        qs = qs.filter(status=status)
    if min_km.isdigit():
        qs = qs.filter(km__gte=int(min_km))
    if max_km.isdigit():
        qs = qs.filter(km__lte=int(max_km))

    allowed_orders = ['modelo', 'placa', 'km', '-km']
    if order not in allowed_orders:
        order = 'modelo'
    qs = qs.order_by(order)

    paginator = Paginator(qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'ADMIN/veiculos/listaVeiculos.html', {
        'veiculos': page_obj,
        'page_obj': page_obj,
        'q': q,
        'status': status,
        'min_km': min_km,
        'max_km': max_km,
        'order': order,
        'status_choices': Veiculo.status_veiculo,
    })

@login_required
@user_passes_test(is_admin)
def adicionar_veiculo(request):
    if request.method == 'POST':
        form = VeiculoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Veículo adicionado com sucesso!')
            return redirect('lista_veiculos')
    else:
        form = VeiculoForm()
    return render(request, 'ADMIN/veiculos/adicionarVeiculo.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def editar_veiculo(request, pk):
    veiculo = get_object_or_404(Veiculo, pk=pk)
    if request.method == 'POST':
        form = VeiculoForm(request.POST, instance=veiculo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Veículo atualizado com sucesso!')
            return redirect('lista_veiculos')
    else:
        form = VeiculoForm(instance=veiculo)
    return render(request, 'ADMIN/veiculos/editarVeiculo.html', {'form': form, 'veiculo': veiculo})

@login_required
@user_passes_test(is_admin)
def deletar_veiculo(request, pk):
    veiculo = get_object_or_404(Veiculo, pk=pk)
    if request.method == 'POST':
        veiculo.delete()
        messages.success(request, 'Veículo excluído com sucesso!')
    
    return redirect('lista_veiculos')
    
@login_required
@user_passes_test(is_admin)
def lista_motoristas(request):
     motoristas = PerfilMotorista.objects.all()
     return render(request, 'ADMIN/motoristas/listaMotoristas.html', {'motoristas': motoristas})

@login_required
@user_passes_test(is_admin)
def lista_entregas(request):
    entregas_lista = Entrega.objects.select_related('cliente', 'veiculo', 'motorista').all()
    filtrar_status = request.GET.get('status', '')
    busca = request.GET.get('q', '')

    if filtrar_status:
        entregas_lista = entregas_lista.filter(status=filtrar_status)

    if busca:
        entregas_lista = entregas_lista.filter(Q(cliente__nome_empresa__icontains=busca)|Q(veiculo__placa__icontains=busca)|Q(motorista__user__first_name__icontains=busca))

    ordenar = request.GET.get('ordenar', '-data_inicio_prevista')

    dados_ordenacao = [
        'data_inicio_prevista', '-data_inicio_prevista',
        'status', '-status',
        'cliente_nome_empresa', '-cliente_nome_empresa'
    ]

    if ordenar in dados_ordenacao:
        entregas_lista = entregas_lista.order_by(ordenar)

    total_por_pagina = Paginator(entregas_lista, 15)
    num_pagina = request.GET.get('page')
    pagina_obj = total_por_pagina.get_page(num_pagina)

    contexto = {
        'entregas': pagina_obj,
        'status_choices': Entrega.STATUS_ENTREGA,
        'current_status': filtrar_status,
        'current_query': busca,
        'current_sort': ordenar,
    }

    return render(request, 'ADMIN/entregas/listaEntregas.html', contexto)

@login_required
@user_passes_test(is_admin)
def lista_manutencoes(request):
    manutencoes = Manutencao.objects.all()
    return render(request, 'ADMIN/manutencoes/listaManutencoes.html', {'manutencoes': manutencoes})

@login_required
@user_passes_test(is_admin)
def alerta_manutencao(request):
    threshold_km = 10000
    threshold_dias = 180

    veiculos_alerta_km = Veiculo.objects.filter(km__gte=models.F('ultimaManutencao_km') + threshold_km)
    veiculos_alerta_dias = Veiculo.objects.filter(ultimaManutencao__lte=timezone.now() - timedelta(days=threshold_dias))

    veiculos_alerta = (veiculos_alerta_km | veiculos_alerta_dias).distinct()

    return render(request, 'ADMIN/manutencoes/alertaManutencao.html', {'veiculos_alerta': veiculos_alerta})

@login_required
@user_passes_test(is_admin)
def alerta_status(request):
    entregas_atrasadas = Entrega.objects.filter(
        data_fim_prevista__lt=timezone.now(),
        status__in=['PENDENTE', 'EM_ROTA']
    )
    return render(request, 'ADMIN/entregas/alertaStatus.html', {'entregas_atrasadas': entregas_atrasadas})


@login_required
@user_passes_test(is_admin)
def coordenadasMapa(request):
    coordenadas = Coordenada.objects.all()
    return render(request, 'ADMIN/entregas/coordenadasMapa.html', {'coordenadas': coordenadas})


# ------------------Views do PerfilMotorista-------------------------------------------------------------------------
def is_motorista(user):
    try:
        user.perfilmotorista
        return True
    except PerfilMotorista.DoesNotExist:
        return False

@login_required
@user_passes_test(is_motorista) #acesso só dos motoristas
def dashboard_motorista(request):
    motorista_perfil = request.user.perfilmotorista
    def _motorista_veiculo_obj(motorista):
        veiculo_str = motorista.veiculoAtual
        if not veiculo_str:
            return None
        try:
            return Veiculo.objects.filter(placa__iexact=veiculo_str).first() or Veiculo.objects.filter(modelo__iexact=veiculo_str).first()
        except Exception:
            return None

    veiculo_atual = _motorista_veiculo_obj(motorista_perfil)
    if veiculo_atual:
        entregas_atribuidas = Entrega.objects.filter(veiculo=veiculo_atual)
    else:
        entregas_atribuidas = Entrega.objects.none()

    return render(request, 'MOTORISTA/dashboard_motorista.html', {'motorista': motorista_perfil, 'entregas_atribuidas': entregas_atribuidas,})

@login_required
@user_passes_test(is_motorista)
def registrar_abastecimento(request):
    if request.method == 'POST':
        form = AbastecimentoForm(request.POST)
        if form.is_valid():
            abastecimento = form.save(commit=False)
            motorista_perfil = request.user.perfilmotorista
            abastecimento.motorista = motorista_perfil
            veiculo_obj = None
            if motorista_perfil.veiculoAtual:
                veiculo_obj = Veiculo.objects.filter(placa__iexact=motorista_perfil.veiculoAtual).first() or Veiculo.objects.filter(modelo__iexact=motorista_perfil.veiculoAtual).first()
            abastecimento.veiculo = veiculo_obj
            abastecimento.save()
            messages.success(request, 'Abastecimento registrado com sucesso!')
            return redirect('dashboard_motorista')
    else:
        form = AbastecimentoForm()
    return render(request, 'MOTORISTA/abastecer.html', {'form': form})


@login_required
@user_passes_test(is_motorista)
def solicitar_manutencao(request):
    if request.method == 'POST':
        form = ManutencaoForm(request.POST) 
        if form.is_valid():
            solicitacao = form.save(commit=False)
            motorista_perfil = request.user.perfilmotorista
            solicitacao.motorista = motorista_perfil
            veiculo_obj = None
            if motorista_perfil.veiculoAtual:
                veiculo_obj = Veiculo.objects.filter(placa__iexact=motorista_perfil.veiculoAtual).first() or Veiculo.objects.filter(modelo__iexact=motorista_perfil.veiculoAtual).first()
            solicitacao.veiculo = veiculo_obj
            solicitacao.status = 'SOLICITADA'
            solicitacao.save()
            messages.success(request, 'Solicitação de manutenção enviada com sucesso!')
            return redirect('dashboard_motorista')
    else:
        form = ManutencaoForm()
    return render(request, 'MOTORISTA/solicitarManutencao.html', {'form': form})

@login_required
@user_passes_test(is_motorista)
def minhas_entregas(request):
    motorista_perfil = request.user.perfilmotorista

    entregas = Entrega.objects.filter(motorista=motorista_perfil, status__in=['ALOCADA', 'EM_ROTA']).select_related('veiculo', 'cliente', 'origem', 'destino').order_by('data_inicio_prevista')
    return render(request, 'MOTORISTA/minhasEntregas.html', {'entregas': entregas})

@login_required
@user_passes_test(is_motorista)
def atualizar_status_entrega(request, pk):
    entrega = get_object_or_404(Entrega, pk=pk)
    motorista_perfil = request.user.perfilmotorista
    veiculo_atual = None
    if motorista_perfil.veiculoAtual:
        veiculo_atual = Veiculo.objects.filter(placa__iexact=motorista_perfil.veiculoAtual).first() or Veiculo.objects.filter(modelo__iexact=motorista_perfil.veiculoAtual).first()
    if not veiculo_atual or entrega.veiculo != veiculo_atual:
        messages.error(request, 'Você não tem permissão para atualizar esta entrega.')
        return redirect('minhas_entregas')

    if request.method == 'POST':
        novo_status = request.POST.get('status')
        if novo_status in ['EM_ROTA', 'ENTREGUE', 'PROBLEMA']:
            entrega.status = novo_status
            if novo_status == 'EM_ROTA' and not entrega.data_inicio_real:
                 entrega.data_inicio_real = timezone.now()
            if novo_status == 'ENTREGUE' and not entrega.data_fim_real:
                 entrega.data_fim_real = timezone.now()

            entrega.save()
            messages.success(request, f'Status da entrega {entrega.id} atualizado para {novo_status}.')
            return redirect('minhas_entregas')

    return render(request, 'MOTORISTA/atualizarStatusEntrega.html', {'entrega': entrega}) 


# ------------------Views do Cliente-------------------------------------------------------------------------

def is_cliente(user):
    try:
        user.perfilcliente
        return True
    except PerfilCliente.DoesNotExist:
        return False

@login_required
@user_passes_test(is_cliente)#acesso só pra cliente
def dashboard_cliente(request):
    cliente_perfil = request.user.perfilcliente
    entregas_cadastradas = Entrega.objects.filter(cliente=cliente_perfil)
    return render(request, 'CLIENTE/dashboard_cliente.html', {'cliente': cliente_perfil, 'entregas_cadastradas': entregas_cadastradas,})

@login_required
@user_passes_test(is_cliente)
def cadastrar_pedido(request):
    if request.method == 'POST':
        form = EntregaForm(request.POST)
        if form.is_valid():
            entrega = form.save(commit=False)
            entrega.cliente = request.user.perfilcliente
            entrega.status = 'PENDENTE'
            entrega.save()

            success, message = Entrega.objects.atribuir_entrega_automatica(entrega)

            if success:
                messages.success(request, f'Ótima notícia! Seu pedido foi cadastrado e já alocado. {message}')
            else:
                messages.info(request, 'Pedido cadastrado com sucesso! Nosso sistema já está buscando o melhor veículo para sua entrega.')
            return redirect('dashboard_cliente')
    else:
        form = EntregaForm()

    return render(request, 'CLIENTE/cadastrarEntrega.html', {'form': form})

@login_required
@user_passes_test(is_cliente)
def meus_pedidos(request):
    cliente_perfil = request.user.perfilcliente
    pedidos = Entrega.objects.filter(cliente=cliente_perfil)
    return render(request, 'CLIENTE/meusPedidos.html', {'pedidos': pedidos})

@login_required
@user_passes_test(is_cliente)
def status_pedido(request, pk):
    pedido = get_object_or_404(Entrega, pk=pk)
    if pedido.cliente != request.user.perfilcliente:
        messages.error(request, 'Você não tem permissão para visualizar este pedido.')
        return redirect('meus_pedidos')

    return render(request, 'CLIENTE/statusPedido.html', {'pedido': pedido})


def register_cliente(request):
    if request.method == 'POST':
        user_form = UserCreationForm(request.POST)
        nome_empresa = request.POST.get('nome_empresa', '')
        endereco = request.POST.get('endereco', '')
        telefone = request.POST.get('telefone', '')
        if user_form.is_valid():
            with transaction.atomic():
                user = user_form.save()
                PerfilCliente.objects.create(
                    user=user,
                    nome_empresa=nome_empresa or None,
                    endereco=endereco or None,
                    telefone=telefone or None,
                )
                try:
                    grupo_cliente, _ = Group.objects.get_or_create(name='Cliente')
                    user.groups.add(grupo_cliente)
                except Exception:
                    pass
                messages.success(request, 'Cadastro realizado com sucesso. Faça login para continuar.')
                return redirect('login')
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
        user_form = UserCreationForm()
    return render(request, 'registration/register_cliente.html', {'user_form': user_form})


@login_required
@user_passes_test(is_admin)
def register_motorista(request):
    if request.method == 'POST':
        user_form = UserCreationForm(request.POST)
        motorista_form = MotoristaForm(request.POST)
        if user_form.is_valid() and motorista_form.is_valid():
            with transaction.atomic():
                user = user_form.save()
                motorista = motorista_form.save(commit=False)
                motorista.user = user
                motorista.save()
                try:
                    grupo, _ = Group.objects.get_or_create(name='Motorista')
                    user.groups.add(grupo)
                except Exception:
                    pass
                messages.success(request, 'Motorista criado com sucesso.')
                return redirect('lista_motoristas')
        else:
            messages.error(request, 'Corrija os erros no formulário.')
    else:
        user_form = UserCreationForm()
        motorista_form = MotoristaForm()
    return render(request, 'ADMIN/motoristas/adicionarMotorista.html', {
        'user_form': user_form,
        'motorista_form': motorista_form,
    })
