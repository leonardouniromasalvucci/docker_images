FROM centos:7

RUN yum -y groupinstall "Development Tools"
RUN yum -y install epel-release wget
RUN yum -y install python36 python36-devel
RUN rpm -Uvh https://github.com/griddb/c_client/releases/download/v4.2.0/griddb_c_client-4.2.0-1.linux.x86_64.rpm
RUN ln -sf /usr/include/python3.6m /usr/include/python3.6

RUN yum -y install python3-pip
RUN pip3 install paho-mqtt
RUN pip3 install pika==1.0.0

ENV PYTHONPATH /usr/src/app

RUN wget https://raw.githubusercontent.com/leonardouniromasalvucci/docker_images/master/producer/producer.py