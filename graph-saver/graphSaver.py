import redis
from neo4j.v1 import GraphDatabase, basic_auth
import os

class GraphSaver:
    def __init__(self, redis_host=None, redis_port=None, neo4j_host=None, neo4j_port=None, root="10000862"):
        self.root = root

        if neo4j_host is None: neo4j_host = os.environ.get('NEO4J_HOST')
        if neo4j_port is None: neo4j_port = os.environ.get('NEO4J_PORT')
        self.graphDriver = GraphDatabase.driver("bolt://" + neo4j_host + ":" + neo4j_port, auth=basic_auth("neo4j", "neo4j"))
        self.session = self.graphDriver.session()

        if redis_host is None: redis_host = os.environ.get('REDIS_HOST')
        if redis_port is None: redis_port = os.environ.get('REDIS_PORT')
        self._dataDb = redis.Redis(host=redis_host, port=redis_port, db=0)

        self._metaInfo = redis.Redis(host=redis_host, port=redis_port, db=1)

    def run(self):
        print("starting graph processing")
        while True:
            self.process()

    def process(self):
        try:
            (key, unprocessed) = self._metaInfo.blpop("graph", timeout=5)
            unprocessed_value = unprocessed.decode()

            persons = self._dataDb.lrange(unprocessed_value, 0, -1)
        except:
            persons = self._dataDb.lrange(self.root, 0, -1)

        persons = [p.decode() for p in persons]
        self.savePersons(persons)

    def savePersons(self, persons):
        with self.session.begin_transaction() as tx:
            for person in persons:
                tx.run("MERGE (r: Person {id: {id1} })"
                       "MERGE (a: Person {id: {id2} })"
                       "MERGE (r)-[:FRIEND]-(a)",
                       {"id1": self.root, "id2": person})
            tx.success = True
        self.session.close()

# db0 = redis.Redis(host="192.168.99.100", port=32768, db=0)
# db1 = redis.Redis()
# pubSub = db1.pubsub()
# pubSub.subscribe("new-id-with-friends")
#
# driver = GraphDatabase.driver("bolt://192.168.99.100:32769", auth=basic_auth("neo4j", "root"))
# session = driver.session()
#
# while True:
#     pass
#
# root = "10000862"
# friends = db0.lrange(root, 0, -1)
#
# with session.begin_transaction() as tx:
#     for friend in friends:
#         tx.run("MERGE (r: Person {id: {id1} })"
#                "MERGE (a: Person {id: {id2} })"
#                "MERGE (r)-[:FRIEND]-(a)",
#                {"id1": root, "id2": friend.decode()})
#     tx.success = True
#
# session.close()
