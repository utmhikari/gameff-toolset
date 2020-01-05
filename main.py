from config import Config
import json
import logger

LOGGER = logger.get_logger('MAIN')


def main():
    cfg = Config()
    cfg.load()
    print(json.dumps(cfg.get(), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
