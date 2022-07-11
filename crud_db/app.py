"""
Application factory module
"""
import logging
import socket

from crud_db_lavrukhin.crud_db.api.db_api import JsonrpcCrud
import aiohttp_cors
from aiohttp import web

from aiopg.sa import create_engine
logger = logging.getLogger('app')


async def on_app_start(app):
    """
    Service initialization on application start
    """
    assert 'config' in app

    app['localhost'] = socket.gethostbyname(socket.gethostname())
    app['engine'] = await create_engine(user='postgres',
                                        database='people_vladimir',
                                        host='192.168.1.245',
                                        password='postgres',
                                        port='5432')


async def on_app_stop():
    """
    Stop tasks on application destroy
    """


def create_app(config: dict = None) -> web.Application:
    app = web.Application()

    # в этой переменной хранится конфиг приложения, с помощью неё при необходимости
    # мы можем получить любые параметры из файла /etc/orbbec-mjpeg-streamer/orbbec-mjpeg-streamer.json
    app['config'] = config

    # в эту переменную мы будем складывать кадры, полученные с камеры в scanner.image_grabber
    app['frame'] = None

    logging.config.dictConfig(config['logging'])

    # Endpoint, на котором мы можем посмотреть mjpeg-поток. Пример http://192.168.1.245:8080/
    app.router.add_route('*', '/jsonrpc/crud_db', JsonrpcCrud)
    app.on_startup.append(on_app_start)
    app.on_shutdown.append(on_app_stop)

    return app
