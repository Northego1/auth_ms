from typing import Literal, Self
from aio_pika.abc import (
    AbstractQueue
)
from consumer.consumer import Consumer
from exceptions import MicroServiceError


class ConsumerPool:
    def __init__(self: Self):
        self.consumer_pool: dict[str, Consumer] = {}


    def create_consumer(
            self: Self,
            consumer_name: str,
            queue_name: str,
            processor_type: Literal['TOPIC', 'DIRECT']
    ):
        if consumer_name in self.consumer_pool:
            raise MicroServiceError(detail='Consumer with this name alredy exists')
        consumer = Consumer(
            queue_name=queue_name,
            processor_type=processor_type,
            consumer_name=consumer_name,
        )
        self.consumer_pool[consumer_name] = consumer
        return consumer

    def get_consumer(self: Self, consumer_name: str) -> Consumer | None:
        return self.consumer_pool[consumer_name]
    

consumer_pool = ConsumerPool()