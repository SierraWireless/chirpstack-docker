# syntax=docker/dockerfile:1
FROM python:3.7-alpine

RUN pip install chirpstack-api

WORKDIR /code
ADD http_server_to_AV.py /code

EXPOSE 8100
CMD ["/code/http_server_to_AV.py"]
