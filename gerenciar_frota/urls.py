
from django.contrib import admin
from django.urls import path
from app.views import index, test, atualizarKm, veiculo, listadetalhes, cadastrarVeiculo

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index),
    path('test', test, name='test'),
    path('listadetalhes/<int:id>', listadetalhes, name='listadetalhes'),
    path('veiculos', veiculo, name='veiculos'),
    path('atualizarKm/<int:id>/', atualizarKm, name='atualizarKm'),
    path('cadastrarVeiculo', cadastrarVeiculo, name='cadastrarVeiculo'),



    
]
