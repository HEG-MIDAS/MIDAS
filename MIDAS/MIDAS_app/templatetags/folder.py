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

@register.filter(name='split')
def split(value, key):
    """
        Returns the value turned into a list.
    """
    return value.split(key)

@register.simple_tag
def breadcrumb(path):
    """
        Returns breadcrumb from given path
    """
    str = ""
    if path == "":
        str+= '<li class="breadcrumb-item">Données</li>'
    else:
        str+= '<li class="breadcrumb-item"><a href="/manage-data/">Données</a></li>'
        path_arr = path.split("/")
        for i in range(0,len(path_arr)):
            str += '<li class="breadcrumb-item">'
            path_name = path_arr[i]
            if path_name == "original":
                path_name = "Données originelles"
            if path_name == "transformed":
                path_name = "Données transformées"
            if(i<len(path_arr)-1):
                url = ""
                for j in range(0,i+1):
                    url += "?" if j == 0 else "&"
                    url += f"path={path_arr[j]}"
                str += f'<a href="/manage-data/{url}">'
            str += f'{path_name}'
            if(i<len(path_arr)-1):
                str += '</a>'
            str += '</li>'
    return str
