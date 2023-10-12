from django import template

register = template.Library()


@register.filter
def reverse(chat_list):
    return chat_list[::-1]
