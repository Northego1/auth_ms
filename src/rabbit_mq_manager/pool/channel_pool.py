
import asyncio
from aio_pika import IncomingMessage
from pamqp.common import Arguments
from typing import Optional, Self, Union

from aio_pika.abc import (
    AbstractChannel,

)
from rabbit_mq_manager.pool.abstract_pool import AbstractPool
from logger import (
    service_logger as serv_log,
)
from rabbit_mq_manager.connection_manager import RabbitMqManager, connection_manager
from exceptions import MicroServiceError


class ChannelPool(AbstractPool):
    def __init__(self: Self):
        self.channel_pool: dict[str, AbstractChannel] = {}

        self.connection: RabbitMqManager = connection_manager


    async def add(
            self: Self,
            name: str = 'base_channel',
            publisher_confirms: bool = True,
            on_return_raises: bool = False
    ) -> AbstractChannel:
        '''
        '''
        if name in self.channel_pool:
            return self.channel_pool[name]
        try:
            serv_log.info(f'Trying to create channel {name!r}')
            channel: AbstractChannel = await self.connection.connection.channel(
                publisher_confirms=publisher_confirms,
                on_return_raises=on_return_raises
            )
            self.channel_pool[name] = channel
            return channel
        except Exception as e:
            serv_log.critical(f'Cant create channel. Error: {e}')
            raise MicroServiceError('Creating channel failed') from e
        
        serv_log.info(f'Channel {name!r} succuss added to pool')


    async def close_all_channels(self: Self):
        for channel in self.channel_pool.values():
            await channel.close()
        serv_log.warning('All channels closed')


    def get(self: Self, name: str):
        try:
            return self.channel_pool[name]
        except Exception:
            serv_log.critical(f'Tried to get not exists channel {name!r}')


channel_pool = ChannelPool()