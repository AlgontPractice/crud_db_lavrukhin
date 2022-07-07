"""
Service running module
"""
import json

import sys
import argparse
from aiohttp import web

from crud_db.app import create_app


def get_config_files():
    """
    Gets configuration profile name

    Returns:
        tuple (service_config)

    """
    parser = argparse.ArgumentParser(description='crud_db service')
    parser.add_argument(
        '--config',
        help='configuration file name',
        type=str,
        default='D:\MyProjects\crud_db_lavrukhin\crud_db.json')  # TODO: в проекте есть файл crud_db.json - его надо положить в папку, указанную тут. При необходимости каталог можно изменить
    args, _ = parser.parse_known_args()

    if not args.config:
        parser.print_usage()
        sys.exit(1)
    return args.config


if __name__ == '__main__':
    config_file = get_config_files()

    with open(config_file) as f:
        config = json.load(f)
    app = create_app(config=config)
    web.run_app(
        app,
        host=config['host'],
        port=config['port'],
        access_log_format=config.get('access_log_format')
    )
