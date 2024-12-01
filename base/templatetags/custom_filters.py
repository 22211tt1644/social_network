from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    """Lấy giá trị từ dictionary theo key"""
    return dictionary.get(key)