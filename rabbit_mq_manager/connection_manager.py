from typing import Self
from aio_pika import connect_robust
from aio_pika.abc import (
    AbstractRobustConnection,
)
from config import settings
from exceptions import MicroServiceError
from logger import service_logger as serv_log




class RabbitMqManager:
    '''
    Класс отвечающий за установление и разрыв соеденения с
    RabbitMq сервером"
    '''
    def __init__(self: Self):
        self.connection = None


    async def connect(self: Self) -> AbstractRobustConnection:
        '''Установливает соеденение с RabbitMq сервером'''
        try:
            serv_log.info('Trying to connect to RabbitMq server')
            self.connection: AbstractRobustConnection = await connect_robust(
                url=settings.rabbit.rabbit_mq_dsn,
                login=settings.rabbit.RMQ_USER,
                password=settings.rabbit.RMQ_PASSWORD
            )
        except Exception as e:
            serv_log.error(f'Cant connect to RabbitMq. Error: {e}')
            raise MicroServiceError('Creating connection failed') from e
        serv_log.info(f'Connected to RabbitMq server {self.connection!r}')
        return self.connection
    

    async def close(self: Self):
        '''Завершает соеденение'''
        if self.connection:
            await self.connection.close()
            serv_log.warning('Connection closed')


connection_manager = RabbitMqManager()