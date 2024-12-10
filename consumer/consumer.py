import asyncio
from aio_pika import IncomingMessage
from aio_pika.abc import (
    AbstractQueue
)
from typing import Literal, Optional, Self, Union

from exceptions import MicroServiceError
from rabbit_mq_manager import pool
from consumer.message_proccessor import DirectProcessor, TopicProcessor
from logger import (
    service_logger as serv_log,
)



class Consumer:
    def __init__(
            self: Self,
            consumer_name: str,
            queue_name: AbstractQueue,
            processor_type: Literal['TOPIC', 'DIRECT']
    ):
        self.consumer_name: str = consumer_name 
        self.processor_type = processor_type

        self.queue = pool.queue_pool.get(queue_name)
        if not self.queue:
            raise MicroServiceError(detail='Очередь не найдена')
        self.endpoints= {}


        match self.processor_type:
            case 'TOPIC':
                self.processor = TopicProcessor()
            case 'DIRECT':
                self.processor = DirectProcessor()


    def task(self: Self, task: str):
        """Декоратор для привязки очереди к функции."""
        def wrapper(func):
            self.endpoints[task] = func
            return func
        return wrapper


    async def _process_message(self: Self, message: IncomingMessage):
        """Вызывает процессор для маршрутизации полученного сообщения"""        
        await self.processor.process(message=message, endpoints=self.endpoints)


    async def _consume(self: Self):
        """Основной цикл потребления сообщений."""

        serv_log.info(f'Consumer {self.consumer_name!r} is listening ...')
        async for message in self.queue:
            async with message.process():
                await self._process_message(message)


    def run(self: Self):
        """Запускает потребителя."""
        serv_log.info(f'Adding {self.consumer_name} to event_loop ...')
        asyncio.create_task(self._consume())




