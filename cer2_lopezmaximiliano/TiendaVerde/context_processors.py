# TiendaVerde/context_processors.py
from . import models

def carrito_count(request):
    if request.user.is_authenticated:
        try:
            cliente = request.user.cliente
            count = sum(item.cantidad for item in cliente.carrito.itemcarrito_set.all())
        except models.Cliente.DoesNotExist:
            count = 0
    else:
        count = 0

    return {'carrito_count': count}

def navbar_context(request):
    return {
        'es_cliente': request.user.groups.filter(name='Cliente').exists() if request.user.is_authenticated else False,
        'es_vendedor': request.user.groups.filter(name='Vendedor').exists() if request.user.is_authenticated else False,
        'es_superadmin': request.user.groups.filter(name='SuperAdmin').exists() if request.user.is_authenticated else False,
    }
