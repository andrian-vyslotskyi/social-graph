import redis


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
