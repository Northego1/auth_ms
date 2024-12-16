
from aio_pika import IncomingMessage
from pamqp.common import Arguments
from typing import Optional, Self, Union

from aio_pika.abc import (
    AbstractChannel,
    AbstractExchange,
    AbstractQueue
)
from rabbit_mq_manager.pool.abstract_pool import AbstractPool
from rabbit_mq_manager.pool.channel_pool import channel_pool
from rabbit_mq_manager.pool.exchange_pool import exchange_pool
from logger import (
    service_logger as serv_log,
)
from exceptions import MicroServiceError



class QueuePool(AbstractPool):
    def __init__(self: Self):
        self.queue_pool: dict[str, AbstractQueue] = {}

        self.channel_pool = channel_pool
        self.exchange_pool = exchange_pool


    async def add(
            self: Self,
            exchange_name: str,
            name: str | None = None,
            routing_key: str | None = None,
            *,
            durable: bool = False,
            exclusive: bool = False,
            passive: bool = False,
            auto_delete: bool = False,
            arguments: Arguments = None,
            timeout: Optional[Union[int, float]] = None
    ) -> AbstractQueue:
        """Определяет queue."""
        if name in self.queue_pool:
            return self.queue_pool[name]
        channel: AbstractChannel = self.channel_pool.get('base_channel')
        exchange: AbstractExchange = self.exchange_pool.get(name=exchange_name)
        serv_log.info(f'Trying to add new queue {name!r}')
        try:
            queue: AbstractQueue = await channel.declare_queue(
                name=name,
                durable=durable,
                exclusive=exclusive,
                passive=passive,
                auto_delete=auto_delete,
                arguments=arguments,
                timeout=timeout,
            )
            await queue.bind(exchange=exchange, routing_key=routing_key)
            self.queue_pool[name] = queue
            serv_log.info(f'Queue {name!r} success added to pool')
            return queue
        except Exception as e:
            serv_log.critical(f'Failed to add new queue {name!r}')
            raise MicroServiceError() from e


    async def bind_to_channel(
            self: Self,
            name: str,
            channel_name: str,
    ) -> None:
        """Привязывает существующую очередь к новому каналу."""
        if name not in self.queue_pool:
            serv_log.critical(f'Queue {name!r} not found in pool for binding')
            raise MicroServiceError(f"Queue {name!r} not found")

        serv_log.info(f'Moving queue {name!r} to channel {channel_name!r}')
        try:
            queue: AbstractQueue = self.queue_pool[name]
            new_channel: AbstractChannel = self.channel_pool.get(channel_name)

            # Просто проверяем существование очереди на новом канале
            await new_channel.declare_queue(
                name=queue.name,
                durable=queue.durable,
                exclusive=queue.exclusive,
                passive=True,  # Указываем, что очередь уже существует
                auto_delete=queue.auto_delete,
            )

            serv_log.info(f'Queue {name!r} successfully bound to channel {channel_name!r}')
        except Exception as e:
            serv_log.critical(f'Failed to bind queue {name!r} to channel {channel_name!r}')
            raise MicroServiceError() from e


    def get(self: Self, name: str):
        try:
            return self.queue_pool[name]
        except Exception:
            serv_log.critical(f'Tried to get not exists queue {name!r}')


queue_pool = QueuePool()