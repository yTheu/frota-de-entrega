import threading, time, random
from .models import Veiculo, Entrega, Coordenada

class VeiculoThread(threading.Thread):
    def criar_entrega():
        pass

    def simular_entrega(veiculo_id, entrega_id):
        try:
            veiculo = Veiculo.objects.get(id=veiculo_id)
            entrega = Entrega.objects.get(id=entrega_id)
            #print("passou aq")

        except (Veiculo.DoesNotExist, Entrega.DoesNotExist):
            print("Erro! Veículo ou entrega não encontrado")
            return
        
        print(f"Simulação com veículo {veiculo.placa}")

        origem = entrega.origem
        destino = entrega.destino
        latitude = origem.latitude
        longitude = origem.longitude
        
        print(f"{origem} -> {destino}")
        print(f"Latitude atual: {latitude}")
        print(f"Logitude atual: {longitude}")

        entrega.status = "EM_ROTA"
        entrega.save()

        veiculo.status_veiculo = "EM_ENTREGA"
        veiculo.save()

        #simular o deslocamento
        for i in range(10):
            latitude += (destino.latitude - latitude) * 0.5
            longitude += (destino.longitude - longitude) * 0.5

            Coordenada.objects.create(latitude, longitude)
            print("Atualizando...")
            print(f"Latitude atual: {latitude}")
            print(f"Logitude atual: {longitude}")

            time.sleep(1)