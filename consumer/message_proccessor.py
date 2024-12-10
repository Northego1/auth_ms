
from abc import ABC, abstractmethod
import asyncio

from aio_pika import IncomingMessage
from exceptions import MicroServiceError
from logger import (
    message_logger as mes_log,
    service_logger as serv_log,
    active_id_var
)



class MessageProcessor(ABC):
    @abstractmethod
    def process(self, message: IncomingMessage, endpoints: dict):
        raise NotImplementedError("Subclasses should implement this method.")


class DirectProcessor(MessageProcessor):
    async def process(self, message: IncomingMessage, endpoints: dict):
        '''
        Логика обработки для direct exchange
        Обрабатывает сообщение, вызывает зарегистрированную функцию.
        '''
        try:
            route: str = message.headers.get('X-Processing-Function')
            if not route:
                raise MicroServiceError()
            #Устанавливаем для логирования в пределах -try except- id
            token = active_id_var.set(message.correlation_id)
            
            mes_log.info("Message received")
            if route in endpoints:
                mes_log.info(f"Processing route: {route!r}")
                #Добавляем в ивент луп функцию для обработки сообщения
                asyncio.create_task(endpoints[route](message))
            else:
                mes_log.warning(f"Unknown route: {route}")

        except Exception as e:
            mes_log.error(f"Error processing message: {e}")
        finally:
            active_id_var.reset(token)



class TopicProcessor(MessageProcessor):
    async def process(self, message: IncomingMessage, endpoints: dict):
        '''
        Логика обработки для topic exchange
        Обрабатывает сообщение, вызывает зарегистрированную функцию.
        '''
        try:
            route = message.routing_key.split('.')[-1]
            #Устанавливаем для логирования в пределах -try except- id
            token = active_id_var.set(message.correlation_id)
            
            mes_log.info("Message received")
            if route in endpoints:
                mes_log.info(f"Processing route: {route!r}")
                #Добавляем в ивент луп функцию для обработки сообщения
                asyncio.create_task(endpoints[route](message))
            else:
                mes_log.warning(f"Unknown route: {route}")

        except Exception as e:
            mes_log.error(f"Error processing message: {e}")
        finally:
            active_id_var.reset(token)





