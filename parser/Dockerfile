FROM python:onbuild

ENV REDIS_HOST='redis' \
	REDIS_PORT='6379' \
	NEO4J_HOST='neo4j' \
	NEO4J_PORT='7687'

ADD requirements.txt /graph/requirements.txt
ADD scanVK.py /graph/scan.py
WORKDIR /graph

ENTRYPOINT ["python", "scan.py", "s"]