from django.contrib import admin
from .models import Veiculo, PerfilMotorista, Manutencao, Abastecimento, Coordenada, Entrega
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import PerfilMotorista, PerfilCliente

class PerfilMotoristaInline(admin.StackedInline):
    model = PerfilMotorista
    can_delete = False
    verbose_name_plural = 'perfil motorista'

class PerfilClienteInline(admin.StackedInline):
    model = PerfilCliente
    can_delete = False
    verbose_name_plural = 'perfil cliente'

class UserAdmin(BaseUserAdmin):
    inlines = (PerfilMotoristaInline, PerfilClienteInline)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Veiculo)
admin.site.register(Manutencao)
admin.site.register(Abastecimento)
admin.site.register(Coordenada)
admin.site.register(Entrega)
