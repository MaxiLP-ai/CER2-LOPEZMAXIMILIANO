# TiendaVerde/urls.py

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('login/', views.VistaLogin, name='vista_login'),  # Página de logeo
    path('restablecerPsw/', views.VistaPsw, name='vista_psw'),  # Página de contraseña
    path('register/', views.VistaRegister, name='vista_register'),  # Página de registro
    path('home/', views.VistaHome, name='vista_home'),  # Página de inicio
    path('catalogo/', views.VistaCatalogo, name='vista_catalogo'),  # Página de la tienda
    path('carrito/agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/', views.VistaCarrito, name='vista_carrito'),
    path('carrito/procesar/', views.procesar_pedido, name='procesar_pedido'),
    path('carrito/cancelar/', views.cancelar_compra, name='cancelar_compra'),

    path('registro/', views.registro_usuario, name='registro_usuario'),
    path('login/usuario/', views.login_usuario, name='login_usuario'),
    path('logout/', views.logout_usuario, name='logout'),

    path('historial_pedidos/', views.VistaHistorialPedidos, name='vista_historial_pedidos'),  # Historial de pedidos del cliente
    path('pedidos/', views.VistaPedidos, name='vista_pedidos'),  # Vista para vendedores
    path('pedidos/<int:pedido_id>/', views.VistaDetallePedido, name='vista_detalle_pedido'),

    path('agregar-producto/', views.agregar_producto, name='agregar_producto'),
    path('editar-producto/<int:producto_id>/', views.editar_producto, name='editar_producto'),
    path('eliminar-producto/<int:producto_id>/', views.eliminar_producto, name='eliminar_producto'),
    path('carrito/eliminar/<int:producto_id>/', views.eliminar_producto_carrito, name='eliminar_producto_carrito'),
]


# Agregar la configuración para servir archivos de medios
if settings.DEBUG:  # Solo en modo de desarrollo
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
