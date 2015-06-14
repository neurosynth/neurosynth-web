# Set the base image to Ubuntu
FROM ubuntu:14.04

# File Author / Maintainer
MAINTAINER Tal Yarkoni

# Add the application resources URL
RUN echo "deb http://archive.ubuntu.com/ubuntu/ $(lsb_release -sc) main universe" >> /etc/apt/sources.list

# Update the sources list
RUN apt-get update

# Install basic applications
RUN apt-get install -y --no-install-recommends tar git curl nano wget dialog net-tools build-essential

# install other non-Python packages: redis, node, MySQL, nginx
RUN apt-get -y --no-install-recommends install redis-server node npm mysql-server nginx

# install coffeescript with Node
RUN npm install -g coffee-script

# Install Python and various packages
RUN apt-get -y --no-install-recommends install python python-dev python-distribute python-pip python-numpy python-scipy python-matplotlib ipython ipython-notebook python-pandas python-sympy python-nose python-mysqldb python-tk

# Add code
ADD . /code

WORKDIR /code

# Get pip to download and install requirements:
RUN pip install -r requirements.txt
