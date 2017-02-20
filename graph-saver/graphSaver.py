import redis
from neo4j.v1 import GraphDatabase, basic_auth
import os

class GraphSaver:
    def __init__(self, redis_host=None, redis_port=None, neo4j_host=None, neo4j_port=None, root="10000862"):
        self.root = root

        if neo4j_host is None: neo4j_host = os.environ.get('NEO4J_HOST')
        if neo4j_port is None: neo4j_port = os.environ.get('NEO4J_PORT')
        uri = "bolt://" + neo4j_host + ":" + neo4j_port
        # token = basic_auth(os.environ.get("NEO4J_USER"), os.environ.get("NEO4J_PASS"))
        self.graphDriver = GraphDatabase.driver(uri)
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
        # try:
        (key, unprocessed) = self._metaInfo.blpop("graph", timeout=1)
        unprocessed_value = unprocessed.decode()

        persons = self._dataDb.lrange(unprocessed_value, 0, -1)
        # except:
            # persons = self._dataDb.lrange(self.root, 0, -1)

        persons = [p.decode() for p in persons]
        print("process " + unprocessed_value)
        self.savePersons(persons)

    def savePersons(self, persons):
        with self.session.begin_transaction() as tx:
            for person in persons:
                tx.run("MERGE (r: Person {id: {id1} })"
                       "MERGE (a: Person {id: {id2} })"
                       "MERGE (r)-[:FRIEND]-(a)",
                       {"id1": self.root, "id2": person})
            tx.success = True

if __name__ == '__main__':
    # os.environ['REDIS_HOST']='localhost'
    # os.environ['REDIS_PORT']='6379'
    # os.environ['NEO4J_HOST']='localhost'
    # os.environ['NEO4J_PORT']='7687'
    # os.environ['NEO4J_USER']='neo4j'
    # os.environ['NEO4J_PASS']='root'

    graph_saver = GraphSaver()
    graph_saver.run()