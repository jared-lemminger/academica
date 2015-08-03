'''
Created on 18/5/2015

@author: luisza
'''

from collections import OrderedDict
from django.utils.safestring import mark_safe
from django import template
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from matricula.models import MenuItem

register = template.Library()

def insert_in_item(item, menu):
    dev = False
    if item['obj'].pk == menu.parent.pk:
        item['children'].append({'obj': menu,
                                             'children': []
                                             })
        dev = True
    else:
        for child in item['children']:
            dev = insert_in_item(child, menu)
            if dev:
                break
    return dev

def get_menu_items(user_auth):
    # FIXME do cache for this 
    menues = MenuItem.objects.filter(publicated=True).order_by('order')
    no_root = []
    dic_menu = OrderedDict()
    for menu in menues:
        if not user_auth and menu.require_authentication:
            continue

        if menu.parent is None:
            dic_menu[menu.pk] = {'obj': menu,
                                 'children': []
                                 }
        else:
            if menu.parent.pk in dic_menu:
                dic_menu[menu.parent.pk]['children'].append({'obj': menu,
                                                 'children': []
                                                 })
            else:
                dev = False
                for x in dic_menu:
                    dev = insert_in_item(dic_menu[x], menu)
                    if dev:
                        break
                if not dev:
                    no_root.append(menu)

    while no_root:
            menu = no_root.pop(0)
            dev = False
            for x in dic_menu:
                dev = insert_in_item(dic_menu[x], menu)
                if dev:
                    break
            if not dev:
                no_root.append(menu)

    return dic_menu

def get_ref_and_ref_display(menu):
    ref = "/"
    ref_display = "I am wrong"
    if menu.type == 0:
        ref = reverse(menu.name)
        ref_display = _(menu.description)
    elif menu.type == 1:
        ref = reverse("academica_pages", args=(menu.name,))
        ref_display = menu.description

    return ref, ref_display

def print_menu_item(menues, is_list=False):
    dev = ""
    if is_list:
        items_menu = zip(range(len(menues)), menues)
    else:
        items_menu = menues.items()

    for key, menu in items_menu:
        ref, ref_display = get_ref_and_ref_display(menu['obj'])
        dev += '<li role="presentation" ><a class="btn btn-success" href="%s"> %s</a>' % (ref, ref_display)
        if menu['children']:
            dev += '<ul class="nav nav-pills" >' + print_menu_item(menu['children'], True) + "</ul>"
        dev += '</li>'

    return dev
@register.simple_tag
def show_menu(user_auth):
    menues = get_menu_items(user_auth)
    css = """
<style>
    #menu ul {padding: 0; margin: 0; padding-top: 5px;}
    #menu li { display: inline; position: relative;}
    #menu ul ul {position: absolute; display: none;margin: 0;}
    #menu ul ul ul { left: 100%; top: 0; width: 300px;}
    #menu li:hover > ul { display: block;}
</style>
    """
    dev = '<div id="menu"><ul class="nav nav-pills" >' + print_menu_item(menues) + "</ul></div>"
    return mark_safe(css + dev)

"""
def show_menu(user_auth):
    if not menues.menu_sort:
        menues.main_menu.sort(key=lambda menu: menu[3], reverse=False)
        menues.menu_sort = True

    dev = '<ul class="nav navbar-nav">'
    for menu in menues.main_menu:
        if not menu[2] or user_auth:
            link = reverse(menu[1]) if menu[4] else menu[1]
            dev += '<li role="presentation" ><a href="%s"> %s</a></li>' % (
                        link, menu[0])
    dev += "</ul>"
    return mark_safe(dev)    
"""

