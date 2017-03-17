import redis
import vk
import pika


class Repository(object):
    def saveDataTo(self, key, data):
        pass

    def getDataFrom(self, key, limit=-1):
        pass

    def getOne(self, key):
        pass


class RedisRepository(Repository):
    def __init__(self, host, port, db):
        self._db = redis.Redis(host, port, db)

    def saveDataTo(self, key, data):
        self._db.rpush(key, data)

    def getDataFrom(self, key, limit=-1):
        self._db.lrange(key, 0, limit)

    def getOne(self, key):
        self._db.blpop(key, timeout=1)


class VkRepository(Repository):
    def __init__(self, app_id=None, login=None, password=None):
        # AuthSession(app_id='5671534', user_login='andrian.ua@mail.ru', user_password='')
        self._vkSession = vk.Session()
        self._api = vk.API(self._vkSession)


class VkFriendsRepository(VkRepository):
    def saveDataTo(self, key, data):
        pass

    def getDataFrom(self, key, limit=-1):
        self._api.friends.get(user_id=key)

    def getOne(self, key):
        self._api.users.get(user_id=key)


class RabbitMqRepository(Repository):
    def __init__(self, host, port):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host, port))
        self._channel = connection.channel()
        self._channel.basic_qos(prefetch_count=1)
        # don't dispatch a new message to a worker until it has processed and acknowledged the previous one

        # make some parameters for queues
        # self._channel.queue_declare(queue='task_queue', durable=True)

    def saveDataTo(self, key, data):
        self._channel.basic_publish(exchange='',
                                    routing_key=key,
                                    body=data,
                                    properties=pika.BasicProperties(
                                        delivery_mode=2  # make message persistent
                                    ))

    def getDataFrom(self, key, limit=-1):
        # self._channel.basic_consume(callback,
        #                             queue=key)
        # self._channel.start_consuming()
        pass