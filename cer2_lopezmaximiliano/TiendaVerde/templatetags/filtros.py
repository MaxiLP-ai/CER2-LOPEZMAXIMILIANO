from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiplica el valor por el argumento."""
    try:
        return value * arg
    except (ValueError, TypeError):
        return 0  # Devuelve 0 si hay un error en la multiplicación
