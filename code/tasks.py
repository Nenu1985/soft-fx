import asyncio

from rabbitmq_utils import async_func


@async_func
async def a_sleep(n):
    '''  Some async function we want to run in background '''
    await asyncio.sleep(n)
    return n


@async_func
async def some_func(a: int, b=1):
    print(a * b)
    return a * b
