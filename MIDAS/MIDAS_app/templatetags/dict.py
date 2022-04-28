from django import template

register = template.Library()

@register.filter
def get_items(dic,key):
    return dic.get(key)
