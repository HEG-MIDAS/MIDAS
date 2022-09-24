import requests

from django import template

register = template.Library()
dic = {'sabra':'https://www.ropag-data.ch/gechairmo/i_extr.php','climacity':'http://www.climacity.org/Axis/'}

@register.simple_tag
def check_type(filename):
    if(filename.endswith('.zip')):
        return 'fa-file-zipper'
    elif(filename.endswith('.csv')):
        return 'fa-file-csv'
    else:
        return 'fa-file'
