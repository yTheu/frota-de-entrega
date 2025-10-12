from django import template

register = template.Library()


@register.filter
def is_motorista(user):
    """Verifica se o usuário pertence ao grupo 'Motorista'."""
    if not user or not user.is_authenticated:
        return False
    try:
        return user.groups.filter(name='Motorista').exists()
    except Exception:
        return False


@register.filter
def is_cliente(user):
    """Verifica se o usuário pertence ao grupo 'Cliente'."""
    if not user or not user.is_authenticated:
        return False
    try:
        return user.groups.filter(name='Cliente').exists()
    except Exception:
        return False
