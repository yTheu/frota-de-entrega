from django.urls import path
from django.contrib import admin
from app import views

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('teste/', views.mapa_rastreio, name='mapa_rastreio'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registrar/', views.registrar_cliente, name='registrar_cliente'),
    path('dashboard/', views.dashboard, name='dashboard'), # manda pro dashboard específico dele

    # url do Administrador (dashboard personalizado)
    path('admin/', views.dashboard_admin, name='dashboard_admin'),
    path('admin/dashboard/', views.dashboard_admin, name='dashboard_admin'),
    path('admin/veiculos/', views.lista_veiculos, name='lista_veiculos'),
    path('admin/veiculos/adicionar/', views.adicionar_veiculo, name='adicionar_veiculo'),
    path('admin/veiculos/detalhes/<int:veiculo_id>', views.detalhes_veiculo, name='detalhes_veiculo'),
    path('admin/veiculos/editar/<int:pk>/', views.editar_veiculo, name='editar_veiculo'),
    path('admin/veiculos/deletar/<int:pk>/', views.deletar_veiculo, name='deletar_veiculo'),

    path('admin/motoristas/', views.lista_motoristas, name='lista_motoristas'),
    path('admin/motoristas/adicionar/', views.register_motorista, name='adicionar_motorista'),
    path('admin/motoristas/detalhes/<int:motorista_id>/', views.detalhes_motorista, name='detalhes_motorista'),
    # path('admin/motoristas/editar/<int:pk>/', views.editar_motorista, name='editar_motorista'), #depois adiciono
    # path('admin/motoristas/deletar/<int:pk>/', views.deletar_motorista, name='deletar_motorista'), #depois adiciono

    path('admin/entregas/', views.lista_entregas, name='lista_entregas'),
    path('admin/entregas/adicionar', views.cadastrar_pedido, name='cadastrar_pedido'),
    path('admin/entregas/detalhes/<int:entrega_id>/', views.detalhes_entrega_admin, name='detalhes_entrega_admin'),
    # path('admin/entregas/editar/<int:pk>/', views.editar_entrega, name='editar_entrega'), #depois adiciono
    # path('admin/entregas/deletar/<int:pk>/', views.deletar_entrega, name='deletar_entrega'), #depois adiciono

    path('admin/rotas/', views.lista_rotas, name='lista_rotas'),
    path('admin/rotas/detalhes/<int:rota_id>/', views.detalhes_rota, name='detalhes_rota'),
    path('admin/rotas/planejar/', views.comecar_planejamento_rotas, name='comecar_planejamento_rotas'),

    path('admin/manutencoes/', views.lista_manutencoes, name='lista_manutencoes'),
    path('admin/manutencoes/veiculos/<int:veiculo_id>', views.iniciar_manutencao_veiculo, name='iniciar_manutencao_veiculo'),
    path('admin/manutencoes/detalhes/<int:manutencao_id>/', views.detalhes_manutencao, name='detalhes_manutencao'),
    path('admin/manutencoes/editar/<int:manutencao_id>/', views.editar_manutencao, name='editar_manutencao'),

    path('admin/alertas/manutencao/', views.alerta_manutencao, name='alerta_manutencao'),
    path('admin/alertas/status/', views.alerta_status, name='alerta_status'),
    path('admin/mapa_coordenadas/', views.coordenadasMapa, name='mapa_coordenadas'),

    # url do PerfilMotorista
    path('motorista/dashboard/', views.dashboard_motorista, name='dashboard_motorista'),
    path('motorista/abastecimento/registrar/', views.registrar_abastecimento, name='registrar_abastecimento'),
    path('motorista/manutencao/solicitar/', views.solicitar_manutencao, name='solicitar_manutencao'),
    path('motorista/minhas_entregas/', views.minhas_entregas, name='minhas_entregas'),
    path('motorista/minhas_entregas/atualizar_status/<int:pk>/', views.atualizar_status_entrega, name='atualizar_status_entrega'),
    path('motorista/rotas/iniciar/<int:rota_id>/', views.iniciar_rota, name='iniciar_rota'),
    path('motorista/rotas/encerrar/<int:rota_id>/', views.encerrar_rota_manual, name='encerrar_rota_manual'),


    # url do Cliente
    path('cliente/dashboard/', views.dashboard_cliente, name='dashboard_cliente'),
    path('cliente/pedidos/cadastrar/', views.cadastrar_pedido, name='cadastrar_pedido'),
    path('cliente/meus_pedidos/', views.meus_pedidos, name='meus_pedidos'),
    path('cliente/meus_pedidos/status/<int:pk>/', views.status_pedido, name='status_pedido'),
    path('api/posicoes-veiculos/', views.get_posicoes_veiculos, name='api_posicoes_veiculos'),
]
