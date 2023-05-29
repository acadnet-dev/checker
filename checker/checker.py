from config import Config
from api import run


if __name__ == '__main__':
    config = Config('config.json')

    run(config.port)