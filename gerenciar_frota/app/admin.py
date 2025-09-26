from django.contrib import admin
from .models import Veiculo, Motorista, Manutencao, Abastecimento, Coordenada, Entrega

admin.site.register(Veiculo)
admin.site.register(Motorista)
admin.site.register(Manutencao)
admin.site.register(Abastecimento)
admin.site.register(Coordenada)
admin.site.register(Entrega)
