FROM python:onbuild

ENV REDIS_HOST='redis' \
	REDIS_PORT='6379' \
	NEO4J_HOST='neo4j' \
	NEO4J_PORT='7687'

ADD requirements.txt /graph/requirements.txt
ADD graphSaver.py /graph/graphSaver.py
WORKDIR /graph

ENTRYPOINT ["python", "graphSaver.py"]