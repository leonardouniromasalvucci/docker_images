FROM python:3.6-slim

RUN yum -y install python3-pip
RUN pip3 install paho-mqtt
RUN pip3 install pika==1.0.0

ENV PYTHONPATH /usr/src/app