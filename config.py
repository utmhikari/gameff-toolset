import json
import logger


ENCODING = 'utf-8'
LOGGER = logger.get_logger('CONFIG')


class Config:
    def __init__(self, config_path):
        self._cfg = dict()
        self._cfg_path = config_path

    def load(self) -> (bool, str):
        try:
            with open(self._cfg_path, encoding=ENCODING) as f:
                cfg = json.loads(f.read())
                if isinstance(cfg, dict):
                    self._cfg = cfg
                    return True, ''
                else:
                    msg = 'Invalid config file content type --- %s! Expected dict!' % type(cfg)
                    LOGGER.warning(msg)
                    return False, msg
        except Exception as e:
            msg = 'Error while loading config! %s' % e
            LOGGER.exception(msg)
            return False, msg

    def save(self, cfg) -> (bool, str):
        if not isinstance(cfg, dict):
            msg = 'Invalid config type --- %s! Expected dict!' % type(cfg)
            LOGGER.warning(msg)
            return False, msg
        self._cfg = cfg
        return True, ''

    def get_instance(self):
        return self._cfg

    def get(self, key):
        return self._cfg.get(key, default=None)

