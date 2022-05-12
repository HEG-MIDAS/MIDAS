from django import template
import datetime

register = template.Library()

@register.simple_tag
def compare(date1,date2):
    if date1 == None or date2 == None:
        return None

    if type(date1) is str:
        date1 = datetime.datetime.strptime(date1,'%Y-%m-%d').date()
    if type(date2) is str:
        date2 = datetime.datetime.strptime(date2,'%Y-%m-%d').date()
    if(date1>date2):
        return False

    return True
