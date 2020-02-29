from lib.table_checker import table_checker as tc


@tc.add_checker('item name exist', ['item'])
def check_item_name_exist(data):
    noname_ids = []
    items = data['item']
    for item in items:
        if 'name' not in item.keys() or not item['name']:
            noname_ids.append(item['id'])
    if len(noname_ids) > 0:
        return {
            'success': False,
            'message': 'found items without name! %s' % noname_ids,
        }
    return {
        'success': True,
    }
