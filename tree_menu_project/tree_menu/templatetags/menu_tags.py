from django import template
from django.urls import resolve
from ..models import MenuItem


register = template.Library()

@register.simple_tag(takes_context=True)
def draw_menu(context, menu_name):
    """
    Возвращает дерево пунктов заданного меню в виде списка узлов:
        [
            {
                'item': MenuItem,
                'children': [ ... ],
                'active': bool,
                'expanded': bool
            },
            ...
        ]
    """
    request = context['request']
    # Определяем текущий URL-name и путь
    resolved = resolve(request.path_info)
    current_url_name = resolved.url_name
    current_path = request.path

    # Один запрос: все пункты меню
    items = list(
        MenuItem.objects
            .filter(menu__name=menu_name)
            .select_related('parent')
    )

    # Построение словаря id->узел
    nodes = {
        item.id: {
            'item': item,
            'children': [],
            'active': False,
            'expanded': False
        }
        for item in items
    }

    # Вложенность: собираем корни и детей
    roots = []
    for node in nodes.values():
        parent_id = node['item'].parent_id
        if parent_id and parent_id in nodes:
            nodes[parent_id]['children'].append(node)
        else:
            roots.append(node)

    # Рекурсия: отметка active/expanded
    def mark(node, parent_expanded=False):
        item = node['item']
        url = item.get_url()
        is_active = (item.url == current_url_name) or (url == current_path)
        any_child_expanded = False
        for child in node['children']:
            if mark(child, parent_expanded or is_active):
                any_child_expanded = True
        node['active'] = is_active
        # expanded = если сам активен, если в нем активеый потомок,
        # либо если это непосредственно родитель активного (first level)
        node['expanded'] = is_active or any_child_expanded or parent_expanded
        return node['expanded']
    
    for root in roots:
        mark(root)

    return {'nodes': roots}
