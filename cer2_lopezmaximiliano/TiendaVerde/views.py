from django.shortcuts import render, redirect, get_object_or_404
from . import models
from . import forms
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.utils.translation import gettext_lazy as _
from .models import Producto  # Asegúrate de tener el modelo Producto importado
from django.contrib.auth.decorators import login_required

# ------------------ Visuales ------------------ #
# Login
def VistaLogin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('vista_home')  # Redirige al usuario a la página de inicio
        else:
            messages.error(request, _('Usuario o contraseña incorrectos.'))
    return render(request, 'TiendaVerdeTemp/login.html', {})

def VistaPsw(request):
    return render(request, 'TiendaVerdeTemp/recuperarPsw.html', {})

def VistaRegister(request):
    return render(request, 'TiendaVerdeTemp/register.html', {})

# Vistas
def VistaHome(request):
    return render(request, 'TiendaVerdeTemp/index.html', {})

def VistaCatalogo(request):
    productos = Producto.objects.all()  # Obtener todos los productos
    return render(request, 'TiendaVerdeTemp/catalogo.html', {'productos': productos})

def VistaCarrito(request):
    # Verificar que el usuario esté autenticado
    if not request.user.is_authenticated:
        return redirect('vista_login')

    # Obtener el cliente asociado al usuario actual
    cliente = models.Cliente.objects.get(usuario=request.user)

    # Obtener o crear el carrito del cliente
    carrito, created = models.Carrito.objects.get_or_create(cliente=cliente)

    # Obtener los ítems del carrito
    items = carrito.itemcarrito_set.all()

    # Calcular el total de todos los productos en el carrito y sus subtotales
    total = 0
    for item in items:
        item.subtotal = item.cantidad * item.producto.precio
        total += item.subtotal

    return render(request, 'TiendaVerdeTemp/carrito.html', {'items': items, 'total': total})



# ------------------ Funciones ------------------ #

def registro_usuario(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirmPassword')

        if password == confirm_password:
            try:
                # Crear el usuario
                user = User.objects.create_user(username=username, email=email, password=password)
                
                # Asignar el usuario al grupo de Clientes
                group = Group.objects.get(name='Cliente')
                user.groups.add(group)

                # Iniciar sesión automáticamente
                login(request, user)
                messages.success(request, _("Cuenta creada con éxito."))
                return redirect('vista_home')  # Redirigir a la página de inicio o donde desees
            except Exception as e:
                messages.error(request, _("Error al crear la cuenta: ") + str(e))
        else:
            messages.error(request, _("Las contraseñas no coinciden."))

    return render(request, 'TiendaVerdeTemp/registro.html')

def login_usuario(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('vista_home')  # Redirige al usuario a la página de inicio
        else:
            messages.error(request, _('Usuario o contraseña incorrectos.'))
    return render(request, 'TiendaVerdeTemp/login.html')

def logout_usuario(request):
    logout(request)
    messages.success(request, _("Has cerrado sesión con éxito."))
    return redirect('vista_home')

def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    
    # Verificar si el usuario es superadministrador
    if request.user.is_superuser:
        cliente, created = models.Cliente.objects.get_or_create(usuario=request.user)
    else:
        # Asegúrate de que el usuario esté asociado a un cliente
        try:
            cliente = request.user.cliente
        except models.Cliente.DoesNotExist:
            messages.error(request, "Debes ser un cliente para agregar productos al carrito.")
            return redirect('vista_catalogo')
    
    # Obtener o crear el carrito del cliente
    carrito, created = models.Carrito.objects.get_or_create(cliente=cliente)

    # Obtener o crear el ítem del carrito
    item_carrito, created = models.ItemCarrito.objects.get_or_create(
        carrito=carrito, producto=producto
    )

    # Incrementar la cantidad si el ítem ya existe
    if not created:
        item_carrito.cantidad += 1
    item_carrito.save()

    messages.success(request, f"{producto.nombre} se agregó al carrito.")
    return redirect('vista_catalogo')

def procesar_pedido(request):
    # Verificar que el usuario esté autenticado y sea un cliente o un superadministrador
    if not request.user.is_authenticated or not (request.user.groups.filter(name='Cliente').exists() or request.user.is_superuser):
        messages.error(request, "No tienes permiso para procesar pedidos.")
        return redirect('vista_home')

    # Obtener el carrito del cliente
    carrito = request.user.cliente.carrito

    if carrito:
        # Crear el pedido inicialmente sin el total
        pedido = models.Pedido.objects.create(cliente=request.user.cliente)
        total_pedido = 0  # Variable para acumular el total del pedido

        # Recorrer todos los items del carrito
        for item in carrito.itemcarrito_set.all():
            producto = item.producto

            # Verificar si hay suficiente stock antes de procesar el pedido
            if producto.stock >= item.cantidad:
                # Descontar el stock
                producto.stock -= item.cantidad
                producto.save()

                # Calcular el total para el producto actual (precio * cantidad)
                total_producto = producto.precio * item.cantidad
                total_pedido += total_producto  # Acumular el total del pedido

                # Crear el detalle del pedido
                models.DetallePedido.objects.create(
                    pedido=pedido,
                    producto=producto,
                    cantidad=item.cantidad,
                    precio_unitario=producto.precio
                )
            else:
                # Si no hay suficiente stock, muestra un mensaje de error
                messages.error(request, f"No hay suficiente stock para el producto: {producto.nombre}. Stock disponible: {producto.stock}")
                return redirect('vista_carrito')

        # Asignar el total calculado al pedido y guardar
        pedido.total = total_pedido
        pedido.save()

        # Eliminar todos los elementos del carrito después de procesar el pedido
        carrito.itemcarrito_set.all().delete()
        messages.success(request, "Tu pedido ha sido procesado con éxito.")
        return redirect('vista_carrito')

    messages.error(request, "Tu carrito está vacío.")
    return redirect('vista_carrito')

def cancelar_compra(request):
    if request.user.is_authenticated:
        try:
            cliente = request.user.cliente
            carrito = cliente.carrito
            carrito.itemcarrito_set.all().delete()  # Elimina todos los productos del carrito
            messages.success(request, "La compra ha sido cancelada.")
        except models.Cliente.DoesNotExist:
            messages.error(request, "No se encontró un cliente asociado a tu cuenta.")
    else:
        messages.error(request, "Debes estar autenticado para cancelar la compra.")
    return redirect('vista_catalogo')  # Redirige al catálogo o a otra vista adecuada

# Vista para mostrar el historial de pedidos del cliente
def VistaHistorialPedidos(request):
    if not request.user.is_authenticated:
        return redirect('vista_login')  # Redirige a login si el usuario no está autenticado

    # Si el usuario es superadministrador, muestra todos los pedidos
    if request.user.is_superuser:
        pedidos = models.Pedido.objects.all()
    else:
        # Si el usuario es cliente, muestra solo sus propios pedidos
        cliente = get_object_or_404(models.Cliente, usuario=request.user)
        pedidos = models.Pedido.objects.filter(cliente=cliente)  # Filtra los pedidos del cliente

    return render(request, 'TiendaVerdeTemp/historial_pedidos.html', {'pedidos': pedidos})

def VistaPedidos(request):
    if not request.user.is_authenticated or not (request.user.groups.filter(name='Vendedor').exists() or request.user.groups.filter(name='SuperAdmin').exists()):
        return redirect('vista_home')  # Redirige si no está autenticado o no es vendedor/superadministrador

    # Obtiene todos los pedidos para el vendedor o superadministrador autenticado
    pedidos = models.Pedido.objects.all()  # Ajusta esto si necesitas filtrar los pedidos de alguna manera

    return render(request, 'TiendaVerdeTemp/pedidos.html', {'pedidos': pedidos})


# Vista para mostrar el detalle de un pedido específico (solo para vendedores)
def VistaDetallePedido(request, pedido_id):
    if not request.user.is_authenticated or not request.user.groups.filter(name='Vendedor').exists():
        return redirect('vista_home')  # Redirige si no está autenticado o no es vendedor

    pedido = get_object_or_404(models.Pedido, id=pedido_id)  # Obtiene el pedido específico
    detalles = models.DetallePedido.objects.filter(pedido=pedido)  # Obtiene los detalles de ese pedido

    return render(request, 'TiendaVerdeTemp/detalle_pedido.html', {'pedido': pedido, 'detalles': detalles})

@login_required
def agregar_producto(request):
    if request.method == 'POST':
        form = forms.ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('vista_catalogo')  # Redirige al catálogo después de agregar
    else:
        form = forms.ProductoForm()
    return render(request, 'TiendaVerdeTemp/agregar_producto.html', {'form': form})

def editar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    if request.method == 'POST':
        form = forms.ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('vista_catalogo')  # Redirige al catálogo después de editar
    else:
        form = forms.ProductoForm(instance=producto)
    return render(request, 'TiendaVerdeTemp/editar_producto.html', {'form': form, 'producto': producto})

def eliminar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    if request.method == 'POST':
        producto.delete()
        return redirect('vista_catalogo')  # Redirige al catálogo después de eliminar
    return render(request, 'TiendaVerdeTemp/eliminar_producto.html', {'producto': producto})

def eliminar_producto_carrito(request, producto_id):
    if request.method == "POST":
        # Obtén el carrito del cliente que está autenticado
        carrito = get_object_or_404(models.Carrito, cliente__usuario=request.user)
        
        # Busca el producto que se desea eliminar
        producto = get_object_or_404(Producto, id=producto_id)

        # Busca el item en el carrito
        item_carrito = get_object_or_404(models.ItemCarrito, carrito=carrito, producto=producto)

        # Elimina el item del carrito
        item_carrito.delete()
        messages.success(request, f'El producto "{producto.nombre}" ha sido eliminado de tu carrito.')

        return redirect('vista_carrito')  # Redirige al carrito después de eliminar