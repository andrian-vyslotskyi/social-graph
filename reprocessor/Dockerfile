FROM python:onbuild

ENV REDIS_HOST='redis' \
	REDIS_PORT='6379' \
	NEO4J_HOST='neo4j' \
	NEO4J_PORT='7687'

RUN curl -o /usr/local/bin/mantra -L https://github.com/pugnascotia/mantra/releases/download/0.0.1/mantra && \
    chmod +x /usr/local/bin/mantra

ADD requirements.txt /graph/requirements.txt
ADD scanVK.py /graph/reprocessor.py
WORKDIR /graph

CMD mantra "0 * * * * ? " python reprocessor.py r