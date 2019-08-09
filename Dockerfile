# Set the base image to Ubuntu
FROM ubuntu:18.04

# File Author / Maintainer
MAINTAINER Tal Yarkoni

# Update the sources list
RUN apt-get update

# Install basic applications
RUN apt-get install -y --no-install-recommends tar git curl nano wget dialog net-tools build-essential sudo

# install other non-Python packages: node, nginx, etc.
RUN DEBIAN_FRONTEND=noninteractive apt-get -y --no-install-recommends install tzdata
RUN apt-get -y --no-install-recommends install redis-server nodejs npm nginx

# Dependencies for the various python libs
RUN apt-get install -y gfortran libopenblas-dev liblapack-dev pkg-config libjpeg8-dev freetype* libfreetype6-dev libpng-dev libpq-dev python3-dev

# install coffeescript with Node
RUN npm config set registry http://registry.npmjs.org/
RUN npm install -g coffeescript

# Install Python and various packages
RUN apt-get -y --no-install-recommends install python3 python3-dev python3-pip python3-numpy python3-scipy python3-matplotlib python3-pandas python3-tk python3-setuptools

RUN pip3 install --upgrade pip

# We'll mount the code directory with docker-compose,
# but we'll need it first to install packages etc.
COPY . /tmp/code

WORKDIR /tmp/code

# Install all Python packages with pip
RUN pip3 install -r requirements.txt
