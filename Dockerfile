FROM debian:jessie

RUN apt-get update && apt-get install -y build-essential python3-dev python3-pip

WORKDIR /code

COPY . .
RUN pip3 install --upgrade pip
RUN pip3 install --upgrade -r requirements.txt

ENV PORT 80
ENV TELE_PORT 8080
EXPOSE ${PORT}
EXPOSE ${TELE_PORT}

CMD ["python3", "kv_store.py"]
