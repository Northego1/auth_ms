from aio_pika import IncomingMessage
from api.v1 import controllers
from logger import message_logger as mes_log
from consumer.consumer import Consumer
from api.v1 import controllers
from consumer.consumer_pool import consumer_pool
from timer import timer


consumer = consumer_pool.get_consumer('auth_consumer')


@consumer.task('register')
@timer
async def handle_register(
    message: IncomingMessage,
):
    async with message.process():
        register_controller: controllers.RegisterUserControllerProtocol = (
            await controllers.RegiserUserController()
        )
        response_register_schema = await register_controller.register_user(
            message=message
        )
        mes_log.info('Executing the task ...')
        if message.reply_to:
            response = response_register_schema.to_message()
            response.correlation_id = message.correlation_id
            mes_log.info('Reply response to "Gateway microservice"'
                        f'by queue {message.reply_to!r}') 
            await message.channel.basic_publish(
                body=response.body,
                properties=response.properties,
                routing_key=message.reply_to
            )
            
            # await message.channel.basic_ack(delivery_tag=message.delivery_tag)

            