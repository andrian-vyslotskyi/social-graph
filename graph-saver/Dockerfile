FROM python:3.6

ENV REDIS_HOST='redis' \
	REDIS_PORT='6379' \
	NEO4J_HOST='neo4j' \
	NEO4J_PORT='7687'

ADD hello.py /graph/hello.py
WORKDIR /graph

ENTRYPOINT ["python", "hello.py"]