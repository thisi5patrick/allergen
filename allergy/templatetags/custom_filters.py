from django import template

register = template.Library()


@register.filter
def range_filter(start: int, end: int) -> range:
    return range(start, end + 1)
