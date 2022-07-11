"""
Application factory module
"""
import logging
import socket
from asyncio import AbstractEventLoop
from crud_db_lavrukhin.crud_db.api.db_api import JSONRPC_crud
import aiohttp_cors
from aiohttp import web

from aiopg.sa import engine, create_engine
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

async def on_app_stop(app):
    """
    Stop tasks on application destroy
    """


# pylint: disable = unused-argument
def create_app(loop: AbstractEventLoop = None, config: dict = None) -> web.Application:
    """
    Creates a web application
    Args:
        loop:
            loop is needed for pytest tests with pytest-aiohttp plugin.
            It is intended to be passed to web.Application, but
            it's deprecated there. So, it remains to avoid errors in tests.
        config:
            dictionary with configuration parameters
    Returns:
        application
    """
    app = web.Application()
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
    })
    app['config'] = config  # в этой переменной хранится конфиг приложения, с помощью неё при необходимости мы можем получить любые параметры из файла /etc/orbbec-mjpeg-streamer/orbbec-mjpeg-streamer.json
    app['frame'] = None  # в эту переменную мы будем складывать кадры, полученные с камеры в scanner.image_grabber
    logging.config.dictConfig(config['logging'])


    app.router.add_route('*', '/jsonrpc/crud_db', JSONRPC_crud)  # endpoint, на котором мы можем посмотреть mjpeg-поток. Пример http://192.168.1.245:8080/

    app.on_startup.append(on_app_start)
    app.on_shutdown.append(on_app_stop)
    return app