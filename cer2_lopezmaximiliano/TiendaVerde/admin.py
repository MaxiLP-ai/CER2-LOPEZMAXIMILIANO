from django.contrib import admin
from . import models

@admin.register(models.Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'stock')
    search_fields = ('nombre',)

@admin.register(models.Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'direccion')
    search_fields = ('usuario__username',)

@admin.register(models.Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'fecha_pedido', 'completado')
    list_filter = ('completado',)
    search_fields = ('cliente__usuario__username',)

@admin.register(models.DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'producto', 'cantidad', 'precio_unitario')

@admin.register(models.Carrito)
class CarritoAdmin(admin.ModelAdmin):
    list_display = ('cliente',)

@admin.register(models.ItemCarrito)
class ItemCarritoAdmin(admin.ModelAdmin):
    list_display = ('carrito', 'producto', 'cantidad')
