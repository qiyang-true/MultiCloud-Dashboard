from django import template
from urllib.parse import urlparse, parse_qs
register = template.Library()


# 自定义模版过滤器
@register.filter(name='times')
def times(number):
    return range(number)

@register.filter
def calc_indent(level):
    return level * 20

@register.filter
def get_role_name(rlist, id):
    return rlist[id]

@register.filter
def set_layui_this(leftid, child_id):
    if leftid == '' or child_id == '':
        return ''
    if int(leftid) == int(child_id):
        return 'class=layui-this'
    else:
        return ''
    
@register.filter
def check_url(str):
    if '?' in str:
        return '&'
    else:
        return '?'


@register.filter(name='get_params')
def get_params(request, args):
    url = request.build_absolute_uri()
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query.replace('?','&'))
    args_params = parse_qs(args)
    
    # print('args_params :',args_params)
    # print('query_params :',query_params)

    data1 = {}
    for key, value in args_params.items():
        data1[key] = value[0]
    data2 = {}
    for key, value in query_params.items():
        data2[key] = value[0]
    data = {}
    data.update(data1)
    data.update(data2)
    # print(data)
    query_str = ''
    for key in data:
        query_str += key+'='+data[key]+'&'
    query_str = '?'+query_str.rstrip('&')
    return query_str


@register.filter(name='format_bytes')
def format_bytes(value):
    try:
        value = float(value)
        for unit in ['B', 'KiB', 'MiB', 'GiB', 'TiB']:
            if abs(value) < 1024.0 or unit == 'TiB':
                return f"{round(value)} {unit}"
            value /= 1024.0
    except (ValueError, TypeError):
        return str(value)
    return f"{round(value)} TiB"


@register.filter(name='format_cpu')
def format_cpu(value):
    try:
        cores = float(value) / 1000.0
        return f"{cores:.3f}"
    except (ValueError, TypeError):
        return str(value)