from lib.table_checker import table_checker as tc


@tc.add_checker('goods item exist', ['item', 'good'])
def check_goods_item(data):
    items = data['item']
    goods = data['good']
    item_ids = set()
    for item in items:
        item_ids.add(item['id'])
    noitem_good_ids = []
    for good in goods:
        if good['item_id'] not in item_ids:
            noitem_good_ids.append(good['id'])
    if len(noitem_good_ids) > 0:
        return {
            'success': False,
            'message': 'found goods with wild items! %s' % noitem_good_ids
        }
    return {
        'success': True
    }
