## Prerequisites

- Install [Docker](https://docs.docker.com/installation/)
1) sudo yum update -y
2) sudo amazon-linux-extras install docker
3) sudo yum install docker
4) sudo service docker start
5) sudo usermod -a -G docker ec2-user
6) sudo systemctl start docker // start at boot

- Install [Compose](https://docs.docker.com/compose/install/)
1) curl -L "https://github.com/docker/compose/releases/download/1.23.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
2) chmod +x /usr/local/bin/docker-compose
3) sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose
4) docker-compose --version

## Installation

Set the environment variable RABBIT_HOST_IP. This should be the host IP you get using e.g. ifconfig.

    $ export RABBIT_HOST_IP=$(hostname -i) //<your host IP - not localhost or 127.0.0.1>  

Start containers

    $ docker-compose up --build