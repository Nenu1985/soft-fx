import asyncio
import functools
import inspect
import json
import os
from asyncio.unix_events import _UnixSelectorEventLoop

from aio_pika import Connection, DeliveryMode, Message, connect


async def connect_to_rabbitmq(loop: _UnixSelectorEventLoop) -> Connection:
    ''' Makes a connection to Broker '''

    broker_url = os.environ.get('BROKER_URL', 'localhost')
    is_connection_established = False
    while not is_connection_established:
        try:
            connection = await connect(f"amqp://guest:guest@{broker_url}/",
                                       loop=loop)
            is_connection_established = True
            print('Connection to Broker is established!!!')
        except ConnectionError as e:
            print(e)
            print('Rabbitmq is not ready, retrying connection...')
            await asyncio.sleep(3)
            continue
    print(" [*] Waiting for messages. To exit press CTRL+C")
    return connection


def caller_name() -> str:
    ''' Defines module which calls async_func '''

    frame = inspect.currentframe()
    frame = frame.f_back.f_back
    code = frame.f_code
    return code.co_filename


def async_func(func):
    ''' Decorator for async tasks to run them in workers '''
    @functools.wraps(func)
    async def inner_function(*args, **kwargs):

        # Here we need to distinguish a caller. If caller is
        # 'new_task' we send a Message to broker
        # Otherwise (called by workers) we run the func to calc and
        # return result to worker

        if 'new_task' in caller_name():
            # Perform connection
            loop = asyncio.get_running_loop()

            connection = await connect_to_rabbitmq(loop)

            # Creating a channel
            channel = await connection.channel()

            # Message contains function's name and arugments
            # It's sent to broker and consumes by worker
            # Worker runs specified function with passed arguments
            message_body = json.dumps(
                {
                    'func_name': func.__name__,
                    'args': args,
                    'kwargs': kwargs
                }
            ).encode()

            # full message object
            message = Message(
                message_body,
                delivery_mode=DeliveryMode.PERSISTENT
            )

            # Sending the message
            await channel.default_exchange.publish(
                message, routing_key="task_queue"
            )

            print(" [x] Sent %r" % message)

            await connection.close()
        else:
            return await func(*args, **kwargs)

    return inner_function
