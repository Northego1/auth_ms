import asyncio
import importlib
import pkgutil

from aio_pika import ExchangeType
from rabbit_mq_manager import pool
from exceptions import MicroServiceError
from rabbit_mq_manager.connection_manager import connection_manager
from logger import service_logger as serv_log
from consumer.consumer_pool import consumer_pool


def load_consumers(package_name: str) -> None:
    '''
    Импортирует все модули внутри указанного пакета.
    Это выполняет декораторы внутри импортируемых модулей.
    
    :param package_name: Имя пакета, содержащего модули с маршрутами.
    '''
    try:
        serv_log.info('Trying to load tasks route endpoints')
        package = importlib.import_module(package_name)
        for _, module_name, _ in pkgutil.iter_modules(package.__path__):
            importlib.import_module(f"{package_name}.{module_name}")
            serv_log.info(f'Loaded module {module_name!r}')
    except Exception as e:
        serv_log.error(f"Failed to load routes from package {package_name}")
        raise MicroServiceError() from e
    serv_log.info(f'Successfully loaded tasks modules')


async def shutdown():
    """
    Корректное завершение приложения:
    закрытие каналов и соединения с RabbitMQ.
    """
    serv_log.warning('Shutting down microservice...')
    try:
        await pool.channel_pool.close_all_channels()
        await connection_manager.close()
        serv_log.warning('Microservice stopped.')
    except Exception as e:
        serv_log.error(f"Error during shutdown: {e}")


async def consumer_setup():
    await pool.exchange_pool.add(
        name='DIRECT',
        type=ExchangeType.DIRECT,
        durable=True,
    )
    await pool.queue_pool.add(
        name='auth.v1',
        exchange_name='DIRECT',
        routing_key='auth.v1'
    )
    auth_consumer = consumer_pool.create_consumer(
        consumer_name='auth_consumer',
        queue_name='auth.v1',
        processor_type='DIRECT'
    )
    auth_consumer.run()


async def main():
    '''
    Устанавливает соединение с RabbitMQ,
    инициализирует всех консьюмеров,
    подгружает декораторы эндпоинтов
    и запускает бесконечный цикл.
    '''
    serv_log.info('Starting microservice...')
    try:
        await connection_manager.connect()
        await pool.channel_pool.add()
        await consumer_setup()

        #Инициализация обрабочиков
        load_consumers('api.v1.receivers')

        # Запуск основного цикла
        while True:
            await asyncio.sleep(3600)

    except Exception as e:
        serv_log.error(f"Error in main loop: {e}")
        await shutdown()
        raise



if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        pass
    finally:

        pending = asyncio.all_tasks(loop=loop)
        for task in pending:
            task.cancel()

        loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
        loop.run_until_complete(shutdown())
        loop.close()
        serv_log.info("Event loop closed.")












