
import asyncio

from tasks import a_sleep, some_func


# a_sleep() is a task we want to run in background
async def main():
    print('Running tasks')
    await a_sleep(1)
    await a_sleep(2)
    await a_sleep(3)
    await a_sleep(4)
    await some_func(3, 4)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
