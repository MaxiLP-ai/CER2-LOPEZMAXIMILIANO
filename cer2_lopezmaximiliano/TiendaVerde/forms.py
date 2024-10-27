from django import forms
from .models import Producto

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio', 'stock', 'imagen']  # Lista los campos que deseas incluir en el formulario

        # Opcional: Personalizar etiquetas o añadir atributos
        labels = {
            'nombre': 'Nombre del Producto',
            'descripcion': 'Descripción',
            'precio': 'Precio',
            'stock': 'Cantidad en Stock',
            'imagen': 'Imagen del Producto',
        }
