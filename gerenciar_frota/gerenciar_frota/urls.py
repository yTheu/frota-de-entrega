from django.contrib import admin
from django.urls import path
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('teste/', views.test, name='test'),

    # Veículos
    path('lista_veiculos/', views.listaVeiculos, name='lista_veiculos'),
    path('veiculos/cadastrar/', views.cadastrarVeiculo, name='cadastrar_veiculo'),
    path('veiculos/detalhes/<int:id>/', views.det, name='detalhes_veiculo'),
    path('veiculos/atualizar-km/<int:id>/', views.atualizarKm, name='atualizar_km'),
    path('veiculos/disponiveis/', views.veiculosDisponiveis, name='veiculos_disponiveis'),

    # Motoristas
    path('lista_motoristas/', views.listaMotoristas, name='lista_motoristas'),
    path('motoristas/cadastrar/', views.cadastrarMotorista, name='cadastrar_motorista'),
    path('motoristas/disponiveis/', views.motoristasDisponiveis, name='motoristas_disponiveis'),

    # Entregas
    path('lista_entregas/', views.listaEntregas, name='lista_entregas'),
    path('entregas/cadastrar/', views.cadastrarEntrega, name='cadastrar_entrega'),
    path('entregas/iniciar/<int:id>/', views.iniciarEntrega, name='iniciar_entrega'),
    path('entregas/concluir/', views.concluirEntrega, name='concluir_entrega'),
    path('entregas/monitorar/<int:id>/', views.monitorarEntrega, name='monitorar_entrega'),
    path('entregas/atualizar-status/<int:id>/', views.atualizarStatus, name='atualizar_status'),
    path('entregas/alerta/', views.alertaStatus, name='alerta_status'),

    # Manutenção
    path('lista_manutencoes/', views.listaManutencoes, name='lista_manutencoes'),
    path('manutencoes/agendar/', views.agendarManutencao, name='agendar_manutencao'),
    path('manutencoes/realizar/', views.realizarManutencao, name='realizar_manutencao'),
    path('manutencoes/proxima/<int:id>/', views.proxManutencao, name='proxima_manutencao'),
    path('manutencoes/verificar/<int:id>/', views.verificarManutencoes, name='verificar_manutencoes'),
    path('manutencoes/alerta/', views.alertaManutencao, name='alerta_manutencao'),

    # Coordenadas e Abastecimento
    path('coordenadas/mapa/', views.coordenadasMapa, name='mapa_coordenadas'),
    path('coordenadas/atualizar/', views.atualizarCoordenada, name='atualizar_coordenada'),
    path('abastecer/', views.abastecer, name='abastecer'),
]
