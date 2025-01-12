FROM bde2020/spark-submit:3.3.0-hadoop3.3

LABEL maintainer="Your Name <your.email@example.com>"

RUN mkdir /app
COPY ./goo.sh /goo.sh

COPY ./spark.py ./hadoop_to_elastics.py ./requirements.txt /app/


WORKDIR /app
RUN pip3 install -r requirements.txt

CMD ["/bin/bash", "/goo.sh"]
