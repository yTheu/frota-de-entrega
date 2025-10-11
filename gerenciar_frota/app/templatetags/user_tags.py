from django import template
from app.models import PerfilMotorista, PerfilCliente # Ajuste o caminho de importação se seu app tiver outro nome

register = template.Library()

@register.filter
def is_motorista(user):
    """Verifica se o usuário tem um PerfilMotorista."""
    if user.is_authenticated:
        try:
            return hasattr(user, 'perfilmotorista') and user.perfilmotorista is not None
        except PerfilMotorista.DoesNotExist:
            return False
    return False

@register.filter
def is_cliente(user):
    """Verifica se o usuário tem um PerfilCliente."""
    if user.is_authenticated:
        try:
            return hasattr(user, 'perfilcliente') and user.perfilcliente is not None
        except PerfilCliente.DoesNotExist:
            return False
    return False
