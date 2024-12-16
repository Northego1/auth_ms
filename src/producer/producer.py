from typing import Optional, Self, Union
from aio_pika.abc import (
    AbstractChannel,
    AbstractQueue
)
from pamqp.common import Arguments
from api.v1.utils.custom_message import CustomMessage
from rabbit_mq_manager import pool
from exceptions import MicroServiceError
from logger import (
    message_logger as mes_log,
)
from logger import service_logger as serv_log



class ProducerManager:
    '''
    '''
    def __init__(self: Self, exchange_name: str):
        self.exchange = pool.exchange_pool.get(exchange_name)
        if not self.exchange:
            raise MicroServiceError('Exchange not defined')
    

    async def get_reply_queue(
            self: Self,
            channel: AbstractChannel | str,
            *,
            durable: bool = False,
            exclusive: bool = True,
            auto_delete: bool = True,
            passive: bool = False,
            arguments: Arguments = None,
            timeout: Optional[Union[int, float]] = None
    ) -> AbstractQueue:
        '''
        Получение временной очереди для ответа на наш запрос.
        '''
        if isinstance(channel, int):
            channel: AbstractChannel = await pool.channel_pool.get(
                name=channel
            )
        try:
            serv_log.debug(f'Trying to create reply queue')
            queue = await channel.declare_queue(
                durable=durable,
                passive=passive,
                exclusive=exclusive,
                auto_delete=auto_delete,
                arguments=arguments,
                timeout=timeout
            )
            serv_log.debug(f'Reply queue  successfully created')
            return queue
        except Exception:
            serv_log.error(f'Creating reply queue is failed')


    async def send(
            self: Self,
            message: CustomMessage,
            routing_key: str | None = None,
            *,
            mandatory: bool = True,
            immediate: bool = False,
            timeout: Optional[Union[int, float]] = None
    ):
        '''
        Обертка для отправки сообщения, нужно передать имя
        уже зарегестрированного exchange_name и message
        '''

        try:
            mes_log.info(f'Trying to send message to {routing_key} ')
            await self.exchange.publish(
                message=message,
                routing_key=routing_key,
                mandatory=mandatory,
                immediate=immediate,
                timeout=timeout
            )
            mes_log.info(f'Message by exchange successfully sent to {routing_key}')
        except Exception as e:
            mes_log.error(f'Sending message by exchange is failed')
            raise MicroServiceError()

    
