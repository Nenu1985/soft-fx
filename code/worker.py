import asyncio
import json

from aio_pika import IncomingMessage

import tasks
from rabbitmq_utils import connect_to_rabbitmq

loop = asyncio.get_event_loop()


async def on_message(message: IncomingMessage):
    ''' Consumer or handler to process incomming messages from a broker

    We know that 'Producer' sends us function name and its arguments to run
    a task here (separate process). Thats why we fetch func_name from a
    message, import function from 'tasks.py'
    '''

    async with message.process():

        # fetching the message's body
        message_body = json.loads(message.body)

        # import function by it's name from the message
        func_to_call = getattr(tasks, message_body.get('func_name'))

        # function's arguments
        args, kwargs = message_body.get('args'), message_body.get('kwargs')

        result = await func_to_call(*args, **kwargs)

        print("     Message body is: %r" % message.body)
        print("     Result is: %r" % result)


async def main():
    # Perform connection
    connection = await connect_to_rabbitmq(loop)

    # Creating a channel
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=1)

    # Declaring queue
    queue = await channel.declare_queue(
        "task_queue",
        durable=True
    )

    print("Waiting for messages. To exit press CTRL+C")

    # Start listening the queue with name 'task_queue'
    await queue.consume(on_message)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main())

    # we enter a never-ending loop that waits for data and runs
    # callbacks whenever necessary.

    loop.run_forever()
