
from aio_pika import ExchangeType, IncomingMessage
from pamqp.common import Arguments
from typing import Optional, Self, Union

from aio_pika.abc import (
    AbstractChannel,
    AbstractExchange
)
from rabbit_mq_manager.pool.abstract_pool import AbstractPool
from rabbit_mq_manager.pool.channel_pool import channel_pool
from logger import (
    service_logger as serv_log,
)
from exceptions import MicroServiceError

class ExchangePool(AbstractPool):
    def __init__(self: Self):
        self.exchange_pool: dict[str, AbstractExchange] = {}

        self.channel_pool = channel_pool


    async def add(
            self: Self,
            name: str,
            type: ExchangeType | str = ExchangeType.DIRECT,
            *,
            durable: bool = False,
            auto_delete: bool = False,
            internal: bool = False,
            passive: bool = False,
            arguments: Arguments = None,
            timeout: Optional[Union[int, float]] = None
    ) -> AbstractExchange:
        '''Определяет exchange'''
        if name in self.exchange_pool:
            return self.exchange_pool[name]
        try:
            channel: AbstractChannel = self.channel_pool.get(name='base_channel')
            serv_log.info(f'Trying to add exchange {name!r}')
            exchange: AbstractExchange = await channel.declare_exchange(
                name=name,
                type=type,
                durable=durable,
                auto_delete=auto_delete,
                internal=internal,
                passive=passive,
                arguments=arguments,
                timeout=timeout, 
            )       
            self.exchange_pool[name] = exchange
        except Exception as e:
            serv_log.error(f'Failed to add new exchange {name!r}')
            raise MicroServiceError() from e
        serv_log.info(f'Exchange {name!r} success added to pool')
        return exchange


    def get(self: Self, name: str):
        try:
            return self.exchange_pool[name]
        except Exception:
            serv_log.critical(f'Tried to get not exists exchange {name!r}')


exchange_pool = ExchangePool()