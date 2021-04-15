#!/bin/bash

sudo yum update -y
sudo amazon-linux-extras -y install docker
sudo amazon-linux-extras install docker
sudo yum -y install docker
sudo service docker start
sudo usermod -a -G docker ec2-user
sudo systemctl start docker
sudo systemctl enable docker

sudo yum -y install git
git clone https://github.com/leonardouniromasalvucci/docker_images.git

sudo curl -L "https://github.com/docker/compose/releases/download/1.23.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose

