
import threading
from datetime import timedelta
import googlemaps
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.core.paginator import Paginator
from django.db import connections, models, transaction
from django.db.models import OuterRef, Q, Subquery
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .forms import AbastecimentoForm, EntregaForm, LoginForm,ManutencaoForm, MotoristaForm, VeiculoForm, RegistroForm
from .models import Abastecimento, Coordenada, Entrega, HistoricoEntrega, Manutencao, PerfilCliente, PerfilMotorista, Rota, Veiculo
from .threads import executar_rota_em_thread

gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY) #inicializa a comunicação com a API

def get_posicoes_veiculos(request):
    veiculos_em_rota = Veiculo.objects.filter(status='EM_ENTREGA').select_related('localizacao_atual')
    
    posicoes = []
    for veiculo in veiculos_em_rota:
        if veiculo.localizacao_atual:
            posicoes.append({
                'id': veiculo.id,
                'placa': veiculo.placa,
                'lat': veiculo.localizacao_atual.latitude,
                'lng': veiculo.localizacao_atual.longitude
            })
            
    return JsonResponse({'veiculos': posicoes})

def mapa_rastreio(request):
    # O contexto que será enviado para o template
    context = {
        # Passando a chave do frontend para o template
        'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY
    }
    return render(request, 'teste.html', context)


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

def registrar_cliente(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            PerfilCliente.objects.create(
                user=user,
                nome_empresa=form.cleaned_data.get('nome_empresa'),
                endereco=form.cleaned_data.get('endereco'),
                telefone=form.cleaned_data.get('telefone')
            )
            
            messages.success(request, 'Cadastro realizado com sucesso! Por favor, faça login para continuar.')
            return redirect('login')
    else:
        form = RegistroForm()
        
    return render(request, 'registration/registrar_cliente.html', {'form': form})

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
    rotas_ativas_count = Rota.objects.filter(status='EM_ROTA').count()
    entregas_para_planejar = Entrega.objects.filter(status='EM_SEPARACAO').count()

    rotas_ativas_list = Rota.objects.filter(status='EM_ROTA').select_related('veiculo', 'motorista').order_by('-data_inicio_real')[:5]
    
    veiculos_com_alerta = []
    for veiculo in Veiculo.objects.all():
        if veiculo.precisa_manutencao():
            veiculos_com_alerta.append(veiculo)

    contexto = {
        'total_veiculos': total_veiculos,
        'total_motoristas': total_motoristas,
        'rotas_ativas_count': rotas_ativas_count,
        'entregas_para_planejar': entregas_para_planejar,
        'rotas_ativas_list': rotas_ativas_list,
        'veiculos_com_alerta': veiculos_com_alerta[:5],
    }
    return render(request, 'ADMIN/dashboard_admin.html', contexto)

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

    contexto = {
        'veiculos': page_obj,
        'page_obj': page_obj,
        'q': q,
        'status': status,
        'min_km': min_km,
        'max_km': max_km,
        'order': order,
        'status_choices': Veiculo.status_veiculo,
    }

    return render(request, 'ADMIN/veiculos/listaVeiculos.html', contexto)

@login_required
@user_passes_test(is_admin)
def detalhes_veiculo(request, veiculo_id):
    veiculo = get_object_or_404(Veiculo, pk=veiculo_id)
    
    rota_ativa = Rota.objects.filter(veiculo=veiculo, status='EM_ROTA').select_related('motorista').first()
    rotas_concluidas = Rota.objects.filter(veiculo=veiculo, status='CONCLUIDA').select_related('motorista').order_by('-data_fim_real')[:10]
    
    historico_manutencao = Manutencao.objects.filter(veiculo=veiculo).order_by('-data')[:10]
    historico_abastecimento = Abastecimento.objects.filter(veiculo=veiculo).order_by('-dataAbastecimento')[:10]
    
    contexto = {
        'veiculo': veiculo,
        'rota_ativa': rota_ativa,
        'rotas_concluidas': rotas_concluidas,
        'historico_manutencao': historico_manutencao,
        'historico_abastecimento': historico_abastecimento,
    }
    
    return render(request, 'ADMIN/veiculos/detalhesVeiculo.html', contexto)

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
    veiculo_ativo_subquery = Rota.objects.filter(
        motorista=OuterRef('pk'), 
        status='EM_ROTA'
    ).values('veiculo__placa')[:1]

    motoristas_lista = PerfilMotorista.objects.annotate(placa_veiculo_atual=Subquery(veiculo_ativo_subquery)).order_by('nome')

    filtrar_disponibilidade = request.GET.get('disponivel', '')
    busca = request.GET.get('q', '')

    if filtrar_disponibilidade:
        esta_disponivel = filtrar_disponibilidade == 'sim'
        motoristas_lista = motoristas_lista.filter(disponivel=esta_disponivel)

    if busca:
        motoristas_lista = motoristas_lista.filter(
            Q(nome__icontains=busca) |
            Q(cpf__icontains=busca) |
            Q(num_cnh__icontains=busca)
        )
    
    paginator = Paginator(motoristas_lista, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    contexto = {
        'motoristas': page_obj,
        'current_disponibilidade': filtrar_disponibilidade,
        'current_query': busca,
    }

    return render(request, 'ADMIN/motoristas/listaMotoristas.html', contexto)

@login_required
@user_passes_test(is_admin)
def detalhes_motorista(request, motorista_id):
    motorista = get_object_or_404(PerfilMotorista, pk=motorista_id)
    
    rota_ativa = Rota.objects.filter(motorista=motorista,status='EM_ROTA').select_related('veiculo').first()
    
    rotas_concluidas = Rota.objects.filter(motorista=motorista,status='CONCLUIDA').select_related('veiculo').order_by('-data_fim_real')[:10]
    
    contexto = {
        'motorista': motorista,
        'rota_ativa': rota_ativa,
        'rotas_concluidas': rotas_concluidas,
    }
    
    return render(request, 'ADMIN/motoristas/detalhesMotorista.html', contexto)

@login_required
@user_passes_test(is_admin)
def lista_entregas(request):
    entregas_lista = Entrega.objects.select_related('cliente', 'destino', 'rota__veiculo', 'rota__motorista').all().order_by('-id')

    filtrar_status = request.GET.get('status', '')
    busca = request.GET.get('q', '')

    if filtrar_status:
        entregas_lista = entregas_lista.filter(status=filtrar_status)

    if busca:
        entregas_lista = entregas_lista.filter(
            Q(cliente__nome_empresa__icontains=busca) |
            Q(rota__veiculo__placa__icontains=busca) |
            Q(rota__motorista__nome__icontains=busca) |
            Q(destino__cidade__icontains=busca)
        )
    
    paginator = Paginator(entregas_lista, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    contexto = {
        'entregas': page_obj,
        'status_choices': Entrega.STATUS_ENTREGA,
        'current_status': filtrar_status,
        'current_query': busca,
    }

    return render(request, 'ADMIN/entregas/listaEntregas.html', contexto)

@login_required
@user_passes_test(is_admin)
def detalhes_entrega_admin(request, entrega_id):
    entrega = get_object_or_404(
        Entrega.objects.select_related(
            'cliente', 'origem', 'destino', 
            'rota__veiculo', 'rota__motorista'
        ),
        pk=entrega_id
    )
    historico_eventos = entrega.historico.all()
    
    contexto = {
        'entrega': entrega,
        'historico': historico_eventos
    }
    return render(request, 'ADMIN/entregas/detalhesEntrega.html', contexto)

@login_required
@user_passes_test(is_admin)
def lista_rotas(request):
    rotas_lista = Rota.objects.select_related('veiculo', 'motorista').all().order_by('-data_criacao')

    filtrar_status = request.GET.get('status', '')

    if filtrar_status:
        rotas_lista = rotas_lista.filter(status=filtrar_status)

    paginator = Paginator(rotas_lista, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    contexto = {
        'rotas': page_obj,
        'status_choices': Rota.status_rota,
        'current_status': filtrar_status,
    }

    return render(request, 'ADMIN/rotas/listaRotas.html', contexto)

@login_required
@user_passes_test(is_admin)
def detalhes_rota(request, rota_id):
    rota = get_object_or_404(Rota.objects.select_related('veiculo', 'motorista').prefetch_related('entregas__cliente', 'entregas__destino'),pk=rota_id)
    
    contexto = {
        'rota': rota,
    }
    
    return render(request, 'ADMIN/rotas/detalhesRota.html', contexto)

def planejar_rotas_em_thread():
    print("Thread de planejamento iniciado")
    try:
        connections.close_all()
        call_command('planejar_rotas')
        print("Thread de planejamento finalizada com sucesso")
    except Exception as e:
        print(f"Erro na thread de planejamento: {e}")

@login_required
@user_passes_test(is_admin)
def comecar_planejamento_rotas(request):
    if request.method == 'POST':
        thread = threading.Thread(target=planejar_rotas_em_thread)
        thread.start()
            
        messages.success(request, "Planejamento de rotas iniciado em segundo plano. Os resultados aparecerão na lista de rotas em breve.")
        return redirect('lista_rotas')
        
    return render(request, 'ADMIN/rotas/planejarRotas.html')

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

def get_rota_ativa_motorista(motorista):
    return Rota.objects.filter(
        motorista=motorista,
        status='EM_ROTA'
    ).select_related('veiculo').first()

@login_required
@user_passes_test(is_motorista)
def dashboard_motorista(request):
    motorista_perfil = request.user.perfilmotorista
    
    rota_ativa = Rota.objects.filter(
        motorista=motorista_perfil,
        status='EM_ROTA'
    ).select_related('veiculo').prefetch_related('entregas__destino').first()

    entregas_na_rota = []
    if rota_ativa:
        entregas_na_rota = rota_ativa.entregas.exclude(status='ENTREGUE').order_by('id')

    contexto = {
        'motorista': motorista_perfil,
        'rota_ativa': rota_ativa,
        'entregas_na_rota': entregas_na_rota,
    }

    return render(request, 'MOTORISTA/dashboard_motorista.html', contexto)

@login_required
@user_passes_test(is_motorista)
def registrar_abastecimento(request):
    motorista_perfil = request.user.perfilmotorista
    rota_ativa = get_rota_ativa_motorista(motorista_perfil)

    if not rota_ativa:
        messages.error(request, "Você precisa estar em uma rota ativa para registrar um abastecimento.")
        return redirect('dashboard_motorista')

    if request.method == 'POST':
        form = AbastecimentoForm(request.POST)
        if form.is_valid():
            abastecimento = form.save(commit=False)
            abastecimento.motorista = motorista_perfil
            abastecimento.veiculo = rota_ativa.veiculo
            abastecimento.save()
            messages.success(request, 'Abastecimento registrado com sucesso!')
            return redirect('dashboard_motorista')
    else:
        form = AbastecimentoForm()
    
    return render(request, 'MOTORISTA/abastecer.html', {'form': form, 'veiculo': rota_ativa.veiculo})


@login_required
@user_passes_test(is_motorista)
def solicitar_manutencao(request):
    motorista_perfil = request.user.perfilmotorista
    rota_ativa = get_rota_ativa_motorista(motorista_perfil)

    if not rota_ativa:
        messages.error(request, "Você precisa estar em uma rota ativa para solicitar uma manutenção.")
        return redirect('dashboard_motorista')

    if request.method == 'POST':
        form = ManutencaoForm(request.POST) 
        if form.is_valid():
            solicitacao = form.save(commit=False)
            solicitacao.motorista = motorista_perfil
            solicitacao.veiculo = rota_ativa.veiculo
            solicitacao.status = 'SOLICITADA'
            solicitacao.save()
            messages.success(request, 'Solicitação de manutenção enviada com sucesso!')
            return redirect('dashboard_motorista')
    else:
        form = ManutencaoForm()
    
    return render(request, 'MOTORISTA/solicitarManutencao.html', {'form': form, 'veiculo': rota_ativa.veiculo})

@login_required
@user_passes_test(is_motorista)
def minhas_entregas(request):
    motorista_perfil = request.user.perfilmotorista

    rotas_do_motorista = Rota.objects.filter(
        motorista=motorista_perfil,
        status__in=['PLANEJADA', 'EM_ROTA']
    ).select_related('veiculo').prefetch_related('entregas__destino')

    contexto = {
        'rotas': rotas_do_motorista,
    }
    
    return render(request, 'MOTORISTA/minhasEntregas.html', contexto)

@login_required
@user_passes_test(is_motorista)
def atualizar_status_entrega(request, pk):
    entrega = get_object_or_404(
        Entrega,
        pk=pk, 
        rota__motorista=request.user.perfilmotorista
    )

    if request.method == 'POST':
        novo_status = request.POST.get('status')
        if novo_status in ['ENTREGUE', 'PROBLEMA']: 
            entrega.status = novo_status
            
            if novo_status == 'ENTREGUE' and not entrega.data_entrega_real:
                entrega.data_entrega_real = timezone.now()

            entrega.save()
            messages.success(request, f'Status da entrega #{entrega.id} atualizado para {novo_status}.')
            return redirect('minhas_entregas')

    return render(request, 'MOTORISTA/atualizarStatusEntrega.html', {'entrega': entrega})

@login_required
@user_passes_test(is_motorista)
def iniciar_rota(request, rota_id):
    if request.method == 'POST':
        # Garante que o motorista só pode iniciar uma rota que é dele
        rota = get_object_or_404(Rota, pk=rota_id, motorista=request.user.perfilmotorista)
        
        if rota.status == 'PLANEJADA':
            # Inicia a thread da simulação em background
            thread = threading.Thread(target=executar_rota_em_thread,args=(rota.id,))
            thread.start()

            messages.success(request, f"Iniciando a Rota #{rota.id}! Bom trabalho!")
        else:
            messages.warning(request, "Esta rota não pode ser iniciada (já está em andamento ou foi concluída).")
            
    # Redireciona de volta para o dashboard, onde ele verá a rota como 'ativa'
    return redirect('dashboard_motorista')

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
    todos_os_pedidos = Entrega.objects.filter(cliente=cliente_perfil).order_by('-data_pedido')
    
    total_pedidos = todos_os_pedidos.count()
    pedidos_em_rota = todos_os_pedidos.filter(status='EM_ROTA').count()
    pedidos_entregues = todos_os_pedidos.filter(status='ENTREGUE').count()
    
    contexto = {
        'cliente': cliente_perfil,
        'entregas_cadastradas': todos_os_pedidos,
        'total_pedidos': total_pedidos,
        'pedidos_em_rota': pedidos_em_rota,
        'pedidos_entregues': pedidos_entregues,
    }
    return render(request, 'CLIENTE/dashboard_cliente.html', contexto)

@login_required
@user_passes_test(is_cliente)
def cadastrar_pedido(request):
    if request.method == 'POST':
        form = EntregaForm(request.POST)
        if form.is_valid():
            try:
                #pega os endereços
                dados = form.cleaned_data
                endereco_origem_txt = f"{dados['rua_origem']}, {dados['numero_origem']} - {dados['bairro_origem']}, {dados['cidade_origem']} - {dados['estado_origem']}, {dados['cep_origem']}"
                endereco_destino_txt = f"{dados['rua_destino']}, {dados['numero_destino']} - {dados['bairro_destino']}, {dados['cidade_destino']} - {dados['estado_destino']}, {dados['cep_destino']}"

                #passa os endereços para a API
                geocode_origem = gmaps.geocode(endereco_origem_txt)
                geocode_destino = gmaps.geocode(endereco_destino_txt)

                #vê se a API encontrou os locais
                if not geocode_origem or not geocode_destino:
                    messages.error(request, "Não foi possível encontrar um ou ambos os endereços. Por favor, verifique e tente novamente.")
                    return render(request, 'CLIENTE/cadastrarEntrega.html', {'form': form})

                #pega as coordenadas
                origem_coords = geocode_origem[0]['geometry']['location']
                coordenada_origem, _ = Coordenada.objects.update_or_create(latitude=origem_coords['lat'], longitude=origem_coords['lng'], defaults={
                        'rua': dados['rua_origem'], 'numero': dados['numero_origem'],
                        'bairro': dados['bairro_origem'], 'cidade': dados['cidade_origem'],
                        'estado': dados['estado_origem'], 'cep': dados['cep_origem'],
                        'endereco_completo': geocode_origem[0]['formatted_address']
                    }
                )

                destino_coords = geocode_destino[0]['geometry']['location']
                coordenada_destino, _ = Coordenada.objects.update_or_create(latitude=destino_coords['lat'], longitude=destino_coords['lng'], defaults={
                        'rua': dados['rua_destino'], 'numero': dados['numero_destino'],
                        'bairro': dados['bairro_destino'], 'cidade': dados['cidade_destino'],
                        'estado': dados['estado_destino'], 'cep': dados['cep_destino'],
                        'endereco_completo': geocode_destino[0]['formatted_address']
                    }
                )

                entrega = form.save(commit=False)
                entrega.cliente = request.user.perfilcliente
                entrega.origem = coordenada_origem
                entrega.destino = coordenada_destino
                entrega.status = 'EM_SEPARACAO'
                entrega.data_entrega_prevista = timezone.now() + timezone.timedelta(days=2)
                entrega.save()

                HistoricoEntrega.objects.create(
                    entrega=entrega,
                    descricao="Pedido realizado e aguardando planejamento de rota."
                )

                messages.success(request, f"Pedido de entrega #{entrega.id} cadastrado com sucesso! Já estamos planejando sua rota.")
                return redirect('dashboard_cliente')
            
            except Exception as e:
                messages.error(request, f"Ocorreu um erro inesperado: {e}")
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
    entrega = get_object_or_404(Entrega, pk=pk, cliente=request.user.perfilcliente)
    historico_eventos = entrega.historico.all()

    contexto = {
        'entrega': entrega,
        'historico': historico_eventos,
    }
    
    return render(request, 'CLIENTE/acompanharEntrega.html', contexto)

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
