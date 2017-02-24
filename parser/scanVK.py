import vk
import redis
from vk.exceptions import VkAPIError
import os
import sys
import pika

UNPROCESSED = "unprocessed"
PROCESSING = "processing"
PROCESSED = "processed"
DENIED = "denied"
GRAPH = "graph"
FAILED = "failed"

class VkProcessor:
    def __init__(self, redis_host=os.environ.get('REDIS_HOST'), redis_port=os.environ.get('REDIS_PORT'),
                 root="34673161"):
        self._root = root

        self._vkSession = vk.Session()
        self._api = vk.API(self._vkSession)
        # AuthSession(app_id='5671534', user_login='andrian.ua@mail.ru', user_password='')

        self._dataDb = redis.Redis(host=redis_host, port=redis_port, db=0)
        self._metaInfoDb = redis.Redis(host=redis_host, port=redis_port, db=1)

        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host = os.environ.get('RABBIT_HOST'),
            port = os.environ.get("RABBIT_PORT")
        ))
        self._channel = connection.channel()
        self._channel.basic_qos(prefetch_count=1)
        #don't dispatch a new message to a worker until it has processed and acknowledged the previous one

    def run(self):
        print("starting scan")
        while (True):
            self.process()

    def process(self):
        try:
            (key, unprocessed) = self._metaInfoDb.blpop(UNPROCESSED, timeout=1)
            unprocessed_value = unprocessed.decode()

            values = self._dataDb.lrange(unprocessed_value, 0, -1)
        except:
            unprocessed_value = self._root
            values = []

        if not values:
            values = self._api.friends.get(user_id=self._root)
            self._dataDb.rpush(self._root, *values)
        else:
            values = [v.decode() for v in values]

        try:
            self.saveFriendsForIds(values)
            self._metaInfoDb.delete(unprocessed_value)
            self._metaInfoDb.rpush(PROCESSED, unprocessed_value)
        except Exception as err:
            print(err)
            self._metaInfoDb.rpush(FAILED, unprocessed_value)
            # self.reprocessFailedIds()

    def saveFriendsForIds(self, values):
        for v in values:
            try:
                friends = self._api.friends.get(user_id=v)  # get friends for id
                processedIds = [id.decode() for id in self._metaInfoDb.lrange(PROCESSED, 0, -1)]
                friends = [f for f in friends if f not in processedIds]
                self._dataDb.rpush(v, *friends)  # save friends if that pair of ids not yet in db
                self._metaInfoDb.rpush(UNPROCESSED, v)

                #set id into collection to mark for graph builder
                self._metaInfoDb.rpush(GRAPH, v)
            except VkAPIError as err:
                if err.code == VkAPIError.ACCESS_DENIED:
                    self._metaInfoDb.rpush(DENIED, err.request_params["user_id"])
                else: print(err)
            except Exception as exception:
                print(exception)
                self._metaInfoDb.rpush(FAILED, v)

    def reprocessFailedIds(self):
        print("starting reprocess")
        failedIds = self._metaInfoDb.blpop(FAILED, timeout=5)
        for failedId in failedIds:
            try:
                allFriends = self._dataDb.lrange(failedId, 0, -1)
                notProcessedFriends = [friend for friend in allFriends if
                                       not self._dataDb.exists(friend)]  # if friend not exist in db
                self.saveFriendsForIds(notProcessedFriends)
                # self._metaInfoDb.delete(failedId)
                self._metaInfoDb.lpush(PROCESSED, failedId)
            except VkAPIError as vkErr:
                if vkErr.code == VkAPIError.ACCESS_DENIED:
                    self._metaInfoDb.rpush(DENIED, vkErr.request_params["user_id"])
            except Exception as err:
                print(err)
                self._metaInfoDb.rpush(FAILED, failedId)


if __name__ == '__main__':
    vkProcessor = VkProcessor()
    if(len(sys.argv) > 0 and str(sys.argv[1]) == "r"):
        vkProcessor.reprocessFailedIds()
    else:
        vkProcessor.run()
