from django import template
from core.models import Person

register = template.Library()

@register.inclusion_tag('tags/person_card.html')
def person_card(slug):
    try:
        person = Person.objects.all().get(slug=slug)
    except Person.DoesNotExist:
        person = None

    return {'person': person}