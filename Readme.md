# Task
Есть корутина

```python
async def some_func(a: int, b=1):
    print( a * b)
```

Есть желание запускать ее в другом процессе (воркере).
Ожидается что появится декоратор 

```python
@async_task
async def some_func(a: int, b=1):
    print( a * b)
```


Т.е. в процессе#1 происходит вызов таски, она сериализуется и попадает в broker(rabbitmq), а в процессе#2(воркере) уже происходит выполнение таски(функции some_func).

Для клиента к rabbitmq рекомендуется использовать https://aio-pika.readthedocs.io/en/latest/
Библиотеки реализующие подобный функционал: celery, https://github.com/Bogdanp/dramatiq

Сильно не усложнять, если занимает много времени. Главное рабочий вариант.

# Description

Application runs some async function in another process. 

*tasks.py* - contains async tasks to run in workers. To make them run in workers wrap each function with
**async_func** decorator

*rabbitmq_utils.py* - contains utils to work with RabbitMQ such as connection and decorator

*worker.py* - Broker's consumer. It reads messages from a broker. In our case messages contain
tasks' name so worker fetch the name, import it from 'tasks.py' module and call the function
to execute and get the result.

*new_task.py* - Simple script juct to call a task from 'tasks.py'. 

# Run app
### Using containers
You can run application inside containers. Just enter

```bash
docker-compose up -d worker
```

A command above runs rabbitmq message broker and a worker (Consumer).
RabbitMQ UI is available on localhost:15672.

After that you need to run a task which you want to run in another process
To do so enter

```bash
docker-compose run task
```

This command sends 4 async tasks to RabbitMQ which are consumed by workers.
You can run several workers to process tasks at the same time. To do it run
another conteiner with a worker and resend tasks to process them by several 
workers

```bash
docker-compose run worker
```

### Another way

Provide execute access to *start_app.sh* and run it

```bash
chmod +x start_app.sh
./start_app.sh
```

### Locally

To run application locally you need to run RabbitMQ (or run a container ```docker run rabbitmq```),
install requirements, run worker (workers) and a task

```bash
python3 -m venv env
. env/bin/activate
pip install -r requiremets.txt
python worker.py
python new_task.py
```

## Troubleshooting

Make sure your RabbitMQ instance contains 'default' and 'default.DQ' queues.
I