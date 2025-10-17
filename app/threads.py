import time
from django.db import connections
from .models import Rota, Coordenada, Veiculo, HistoricoEntrega
from django.utils import timezone
import googlemaps
import random
from django.conf import settings


class frufru:
    CIANO = '\033[96m'
    VERDE = '\033[92m'
    AMARELO = '\033[93m'
    VERMELHO = '\033[91m'
    MAGENTA = '\033[95m'
    AZUL = '\033[94m'
    FIM = '\033[0m'

    CORES_ROTAS = [CIANO, VERDE, AMARELO, MAGENTA, AZUL]

def executar_rota_em_thread(rota_id):
    connections.close_all()
    gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)

    cor_da_rota = random.choice(frufru.CORES_ROTAS)
    
    try:
        rota = Rota.objects.select_related('veiculo', 'motorista').get(id=rota_id)
        veiculo = rota.veiculo
    except Rota.DoesNotExist:
        print(f"{frufru.VERMELHO}[Thread] Erro: Rota {rota_id} não encontrada.{frufru.FIM}")
        return

    log_prefix = f"{cor_da_rota}[ROTA #{rota.id} | VEÍCULO {veiculo.placa}]{frufru.FIM}"

    print(f"{log_prefix} {frufru.VERDE}ROTA INICIADA.{frufru.FIM} Motorista: {rota.motorista.nome}. Entregas: {rota.entregas.count()}. Tempo Estimado: {rota.data_fim_prevista}")

    rota.status = 'EM_ROTA'
    rota.data_inicio_real = timezone.now()
    rota.save()
    veiculo.status = 'EM_ENTREGA'
    veiculo.save()
    rota.motorista.disponivel = False
    rota.motorista.save()
    print(f"PFVR FUNCIONA: Salvei o veículo {veiculo.placa} com o status '{veiculo.status}' !!!")
    
    for entrega in rota.entregas.all():
        entrega.status = 'EM_ROTA'
        entrega.save()
        HistoricoEntrega.objects.create(
            entrega=entrega,
            descricao=f"Seu pedido saiu para entrega com o veículo de placa {veiculo.placa} e motorista {rota.motorista.nome}."
        )
    
    if rota.trajeto_polyline:
        pontos_do_trajeto = googlemaps.convert.decode_polyline(rota.trajeto_polyline)
        total_de_pontos = len(pontos_do_trajeto)
        print(f"{log_prefix} Trajeto definido com {total_de_pontos} pontos geográficos.")
        
        porcentagem_compreesao = 0.01
        duracao_real_em_minutos = rota.duracao_estimada_minutos or 60
        duracao_total_simulacao = (duracao_real_em_minutos * 60) *porcentagem_compreesao

        if total_de_pontos > 0:
            sleep_por_ponto = duracao_total_simulacao / total_de_pontos
        else:
            sleep_por_ponto = 1

        print(f"{log_prefix} Duração real estimada: {duracao_real_em_minutos} min. Simulando em {duracao_total_simulacao:.1f} segundos ({porcentagem_compreesao*100}% do tempo real).")
        
        pontos_para_logar = [int(total_de_pontos * p / 100) for p in range(0, 101, 10)] #mostrar o progresso

        cidade_atual_reportada = None
        PONTOS_PARA_VERIFICAR_CIDADE = 50

        for i, ponto in enumerate(pontos_do_trajeto):
            #atualiza as coordenadas do veículo no bd
            nova_localizacao, _ = Coordenada.objects.get_or_create(latitude=ponto['lat'], longitude=ponto['lng'])
            veiculo.localizacao_atual = nova_localizacao
            veiculo.save()
            
            #mostrar o percentual percorrido
            if i in pontos_para_logar:
                percentual_progresso = ((i + 1) / total_de_pontos) * 100
                print(f"{log_prefix} {frufru.AMARELO}Progresso: {percentual_progresso:.0f}%...{frufru.FIM}")
            
            if i > 0 and i % PONTOS_PARA_VERIFICAR_CIDADE == 0:
                try:
                    reverse_geocode_result = gmaps.reverse_geocode((ponto['lat'], ponto['lng']))
                    nova_cidade = next((comp['long_name'] for comp in reverse_geocode_result[0]['address_components'] if 'locality' in comp['types']), None)
                    
                    if nova_cidade and nova_cidade != cidade_atual_reportada:
                        print(f"{log_prefix} {frufru.CIANO}CHECKPOINT: Veículo passando por {nova_cidade}.{frufru.FIM}")
                        for entrega in rota.entregas.all():
                            HistoricoEntrega.objects.create(entrega=entrega, descricao=f"Seu pedido está passando por {nova_cidade}.")
                        cidade_atual_reportada = nova_cidade
                except Exception as e:
                    print(f"{log_prefix} {frufru.VERMELHO}Erro no Reverse Geocoding: {e}{frufru.FIM}")

            time.sleep(sleep_por_ponto)
            
    else: 
        print(f"{log_prefix} {frufru.AMARELO}Sem trajeto detalhado. Simulando tempo total...{frufru.FIM}")
        time.sleep(60)

    # Rota concluída e enceerra a thread
    print(f"{log_prefix} {frufru.VERDE}ROTA CONCLUÍDA.{frufru.FIM}")
    rota.status = 'CONCLUIDA'
    rota.data_fim_real = timezone.now()
    rota.save()
    veiculo.status = 'DISPONIVEL'
    veiculo.save()
    rota.motorista.disponivel = True
    rota.motorista.save()
    
    for entrega in rota.entregas.all():
        entrega.status = 'ENTREGUE'
        entrega.save()
        HistoricoEntrega.objects.create(entrega=entrega, descricao="Seu pedido foi entregue com sucesso!")