import logger
import os
import pprint

LOGGER = logger.get_logger('TABLE_CHECKER')


class TableChecker:
    """
    check if table data is valid
    """
    def __init__(self):
        self._names = set()
        self._pipeline = []

    def add_checker(self, name, types):
        """
        add a checker function
        :param name: checker name
        :param types: data types used by checker
        :return: checker function decorator
        """
        def wrapper(func):
            if name in self._names:
                LOGGER.warning('Existed Table Check Rule: %s!' % name)
            else:
                LOGGER.info('Importing Table Check Rule: %s...' % name)
                self._names.add(name)
                self._pipeline.append({
                    'name': name,
                    'types': types,
                    'callback': func
                })
        return wrapper

    def get_types(self):
        """
        get all needed data types for check
        :return: types
        """
        types = set()
        for pp in self._pipeline:
            for t in pp['types']:
                types.add(t)
        return sorted(list(types))

    def output(self):
        """
        output checker info
        :return: None
        """
        l = len(self._pipeline)
        s = 'Overall %d Table Checkers:\n' % l
        for i in range(l):
            s += '%d. %s (%s)\n' % (
                i + 1, self._pipeline[i]['name'], self._pipeline[i]['types'])
        LOGGER.info(s)

    def check(self, data):
        LOGGER.info('Start checking table!!!!!!!')
        for pp in self._pipeline:
            LOGGER.info('Checking %s...' % pp['name'])
            try:
                ret = pp['callback'](data)
                LOGGER.info('Result of %s:\n%s' % (
                    pp['name'], pprint.pformat(ret, indent=2, width=60)))
            except Exception as e:
                LOGGER.exception('Failed to check %s! %s' % (pp['name'], e))


table_checker = TableChecker()


def load_checkers(root_dir):
    script_paths = list(filter(
        lambda k: k.endswith('.py') and k != '__init__py', os.listdir(root_dir)))
    LOGGER.info('Loading checkers: %s' % script_paths)
    for script_path in script_paths:
        try:
            content = open(os.path.join(root_dir, script_path)).read()
            exec(content)
        except Exception as e:
            LOGGER.exception('Error while loading checker %s! %s' % (script_path, e))
    table_checker.output()



