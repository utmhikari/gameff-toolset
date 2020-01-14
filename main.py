from config import Config
import json
import logger

LOGGER = logger.get_logger('MAIN')
CONFIG_FILE = './config.py'


def main():
    cfg = Config(config_path=CONFIG_FILE)
    cfg.load()
    print(json.dumps(cfg.get_instance(), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
