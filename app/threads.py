# seu_app/threads.py
import time
from django.db import connections
from .models import Rota

def executar_rota_em_thread(rota_id):
    connections.close_all()
    
    try:
        rota = Rota.objects.get(id=rota_id)
    except Rota.DoesNotExist:
        print(f"[Thread] Erro: Rota {rota_id} não encontrada.")
        return

    print(f"[Thread da Rota #{rota.id}] Executando plano. Duração estimada: {rota.duracao_estimada_minutos} min.")

    rota.status = 'EM_ROTA'
    rota.data_inicio_real = time.timezone.now()
    rota.save()
    rota.veiculo.status = 'EM_ENTREGA'
    rota.veiculo.save()
    rota.motorista.disponivel = False
    rota.motorista.save()
    rota.entregas.all().update(status='EM_ROTA')
    
    if rota.duracao_estimada_minutos:
        tempo_real_de_simulacao_segundos = rota.duracao_estimada_minutos
    else:
        tempo_real_de_simulacao_segundos = 15

    # Futuramente, em vez de um sleep único, você pode iterar sobre os waypoints
    # salvos no 'dados_trajeto_json' e dar um sleep proporcional entre cada um,
    # atualizando a 'localizacao_atual' do veículo a cada passo.
    
    print(f"[Thread da Rota #{rota.id}] Trajeto em andamento... (simulação levará {tempo_real_de_simulacao_segundos:.1f}s)")
    time.sleep(tempo_real_de_simulacao_segundos)

    print(f"[Thread da Rota #{rota.id}] Rota finalizada.")
    rota.status = 'CONCLUIDA'
    rota.data_fim_real = time.timezone.now()
    rota.save()