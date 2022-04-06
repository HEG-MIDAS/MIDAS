import requests

from django import template

register = template.Library()

@register.simple_tag
def sources():
    dic = {'SABRA':'https://www.ropag-data.ch/gechairmo/i_extr.php','ClimaCity':'http://www.climacity.org/Axis/'}
    count = 0
    for k in dic:
        try:
            resp = requests.get(dic[k])
            if resp.status_code != 200:
                count+=1
        except:
            count+=1
    if(count == 0):
        return '<i class="fa-solid fa-circle-check"></i>'
    elif(count != 0 and count < len(dic)):
        return '<i class="fa-solid fa-circle-exclamation"></i>'
    else:
        return '<i class="fa-solid fa-circle-xmark"></i>'
