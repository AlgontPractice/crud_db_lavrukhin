"""
Application factory module
"""
import asyncio
import logging
import logging.config
import socket
from asyncio import AbstractEventLoop

import aiohttp_cors
from aiohttp import web





logger = logging.getLogger('app')


async def task_init_device(scanner_port: Scanner):
    """
    Task for init camera

    Args:
        :param scanner_port:
    """
    while True:
        await asyncio.sleep(1)
        try:
            await scanner_port.init_device()  # пытаемся подключиться к камере раз в секунду
            break
        except Exception:  # pylint: disable = broad-except
            logger.exception('Error init video stream')


# pylint: disable = too-many-statements
async def on_app_start(app):
    """
    Service initialization on application start
    """
    assert 'config' in app

    app['localhost'] = socket.gethostbyname(socket.gethostname())

    try:
        logger.debug('Init camera'),
        await app['scanner'].init_device()  # инициализируем подключение к камере
    except Exception:  # pylint: disable = broad-except
        logger.exception('Error init video streams')
        asyncio.ensure_future(task_init_device(app['scanner']))  # если по какой-то причине произошла ошибка при подключении к камере - пытаемся к ней подключиться в методе task_init_device

    asyncio.ensure_future(app['scanner'].image_grabber(app))  # запускаем корутину для получения кадров с камеры


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
    app['config'] = config  # в этой переменной хранится конфиг приложения, с помощью неё при необходимости мы можем получить любые параметры из файла /etc/orbbec-mjpeg-streamer/crud_db.json
    app['frame'] = None  # в эту переменную мы будем складывать кадры, полученные с камеры в scanner.image_grabber
    logging.config.dictConfig(config['logging'])
    scanner = Scanner(config['video_params'])  # инициализируем класс, в котором реализовано общение с камерой

    app['scanner'] = scanner
    app['camera_service'] = MjpegHandlerService()

    cors.add(app.router.add_route('GET', '/people_onion', app['camera_service'].mjpeg_handler_rgb))  # endpoint, на котором мы можем посмотреть mjpeg-поток. Пример http://192.168.1.245:8080/

    app.on_startup.append(on_app_start)
    app.on_shutdown.append(on_app_stop)
    return app
