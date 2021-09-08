
from django import template
register = template.Library()


@register.simple_tag
def get_verbose_field_name(instance, field_name):
    """
    Returns verbose_name for a field.
    """
    return instance._meta.get_field(field_name).verbose_name.title()
# в template вставляю это - появляется ошибка,
#  что str object has no atribute _meta
# {% load verbose_names %}
# {% get_verbose_field_name post_instance "text" %}
