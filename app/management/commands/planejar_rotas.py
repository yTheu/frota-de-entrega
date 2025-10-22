from django.core.management.base import BaseCommand
from django.utils import timezone
from math import radians, cos, sin, asin, sqrt
from app.models import Entrega, Rota, HistoricoEntrega
from django.conf import settings
import googlemaps

def calcular_distancia_haversine(coord1, coord2):
    lon1, lat1, lon2, lat2 = map(radians, [coord1.longitude, coord1.latitude, coord2.longitude, coord2.latitude])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371
    return c * r

def agrupar_entregas_por_proximidade(entregas, raio_max_km=200):
    clusters = []
    entregas_restantes = list(entregas)

    while entregas_restantes:
        ponto_de_partida = entregas_restantes.pop(0)
        novo_cluster = [ponto_de_partida]
        
        entregas_proximas = [e for e in entregas_restantes if calcular_distancia_haversine(ponto_de_partida.destino, e.destino) <= raio_max_km]
        
        for proxima in entregas_proximas:
            novo_cluster.append(proxima)
            entregas_restantes.remove(proxima)
            
        clusters.append(novo_cluster)
        
    return clusters #grupo com entregas

def chamar_google_maps_api(cluster_de_entregas):
    try:
        gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY) #inicializa a comunicação com a API

        origem_coord = f"{cluster_de_entregas[0].origem.latitude},{cluster_de_entregas[0].origem.longitude}"
        destino_coord = f"{cluster_de_entregas[-1].destino.latitude}, {cluster_de_entregas[-1].destino.longitude}"
        waypoints = [f"{e.destino.latitude},{e.destino.longitude}" for e in cluster_de_entregas]

        directions_result = gmaps.directions(
            origin=origem_coord,
            destination=origem_coord,
            waypoints=waypoints,
            optimize_waypoints=True #o Google decide a melhor rota
        )

        if not directions_result:
            print(f" > Sem resulatdos da API")
            return None
        
        rota_principal = directions_result[0]
        if 'overview_polyline' in rota_principal and 'points' in rota_principal['overview_polyline']:
            polyline = rota_principal['overview_polyline']['points']
            print(f"  > DIAGNÓSTICO: Polyline EXTRAÍDA com sucesso! (Início: {polyline[:30]}...)")
        else:
            print("  > DIAGNÓSTICO: ERRO! A chave 'overview_polyline' não foi encontrada na resposta da API.")
            polyline = None # Garante que não vai quebrar
        polyline = rota_principal['overview_polyline']['points']
        distancia_total_metros = sum(leg['distance']['value'] for leg in rota_principal['legs'])
        duracao_total_segundos = sum(leg['duration']['value'] for leg in rota_principal['legs'])

        return {
            'distancia_km': round(distancia_total_metros / 1000, 2),
            'duracao_minutos': round(duracao_total_segundos / 60),
            'trajeto_polyline': polyline
        }

    except Exception as e:
        print(f" > ERRO AO CHAMAR A APIS DO GOOGLE: {e}")
        return None
    
#gerenciar
class Command(BaseCommand):
    help = 'Analisa entregas em separação, agrupa por proximidade e cria rotas otimizadas.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS(f"[{timezone.now()}] Iniciando o planejamento de rotas..."))

        entregas_em_espera = Entrega.objects.filter(status='EM_SEPARACAO').order_by('data_pedido')
        if not entregas_em_espera:
            self.stdout.write("Nenhuma entrega em separação.")
            return

        clusters = agrupar_entregas_por_proximidade(entregas_em_espera, raio_max_km=50)
        self.stdout.write(f"Encontrados {len(clusters)} clusters de entrega.")

        for i, cluster in enumerate(clusters):
            self.stdout.write(f"Analisando Cluster #{i+1} com {len(cluster)} entregas...")

            if len(cluster) < 2:
                self.stdout.write(f"  > Cluster #{i+1} pequeno demais. Aguardando mais entregas na região.")
                continue

            dados_da_api = chamar_google_maps_api(cluster)
            if not dados_da_api:
                self.stdout.write(self.style.ERROR(f"  > FALHA ao obter dados do Google Maps para este cluster."))
                continue
            
            if dados_da_api.get('trajeto_polyline'):
                print(f"  > DIAGNÓSTICO: O dicionário 'dados_da_api' CONTÉM a polyline.")
            else:
                print(f"  > DIAGNÓSTICO: ERRO! O dicionário 'dados_da_api' NÃO contém a polyline antes de chamar o Manager.")

            ids_das_entregas = [entrega.id for entrega in cluster]
            
            success, message = Rota.objects.criar_rota(
                ids_entregas=ids_das_entregas,
                dados_api=dados_da_api
            )

            if success:
                self.stdout.write(self.style.SUCCESS(f"  > SUCESSO! {message}"))

                # pra registrar os log e acompanhar o histórico do processo de entrega ("Saiu de tal lugar", "Chegou a tal lugar...")
                for entrega in cluster:
                    HistoricoEntrega.objects.create(
                        entrega=entrega,
                        descricao="Seu pedido foi processado e alocado a uma rota de entrega."
                    )
                self.stdout.write(self.style.SUCCESS(f"  > Histórico de rastreamento atualizado para {len(cluster)} entregas."))
            else:
                self.stdout.write(self.style.ERROR(f"  > Ops, falhou aqui! {message}"))