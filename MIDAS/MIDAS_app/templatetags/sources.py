import requests

from django import template

register = template.Library()

@register.simple_tag
def all_status():
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
        return '<i class="status fa-solid fa-circle-check" data-bs-toggle="tooltip" data-bs-placement="bottom" title="Toutes les sources sont opérationnelles"></i>'
    elif(count != 0 and count < len(dic)):
        return '<i class="status fa-solid fa-circle-exclamation" data-bs-toggle="tooltip" data-bs-placement="bottom" title="Certaines sources ne sont pas accessibles"></i>'
    else:
        return '<i class="status fa-solid fa-circle-xmark" data-bs-toggle="tooltip" data-bs-placement="bottom" title="Aucune des sources n\'est accessible"></i>'
