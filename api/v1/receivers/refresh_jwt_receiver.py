import json
import pickle
from re import A
from aio_pika import IncomingMessage
from logger import message_logger as mes_log
from consumer.consumer import Consumer
from pydantic_schemas.response_schemas.auth_service_responses import MsResponseRefreshJwtSchema
from api.v1 import controllers
from consumer.consumer_pool import consumer_pool


consumer = consumer_pool.get_consumer('auth_consumer')



@consumer.task('refresh_jwt')
async def handle_refresh_jwt(
    message: IncomingMessage,
):
    login_user_controller: controllers.RefreshJwtControllerProtocol = (
        await controllers.RefreshJwtController()
    )
    mes_log.info('Executing the task ...')
    response_login_schema = await login_user_controller.refresh_access_token(
        message=message
    )
    if message.reply_to:
        response = response_login_schema.to_message()
        response.correlation_id = message.correlation_id
        mes_log.info('Reply response to "Gateway microservice"'
                    f'by queue {message.reply_to!r}') 
        await message.channel.basic_publish(
            body=response.body,
            properties=response.properties,
            routing_key=message.reply_to
        )
        
        await message.channel.basic_ack(delivery_tag=message.delivery_tag)
        