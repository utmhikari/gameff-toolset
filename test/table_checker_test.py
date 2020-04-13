from lib.table_checker import load_checkers, table_checker

data = {
    'item': [
        {'id': 1, 'name': 'haha'},
        {'id': 2, 'name': 'hehe'},
        {'id': 3, 'name': ''}
    ],
    'good': [
        {'id': 900001, 'item_id': 2},
        {'id': 900002, 'item_id': 4}
    ]
}


if __name__ == '__main__':
    load_checkers('./test/table_checker')
    table_checker.check(data)
