# Set the base image to Ubuntu
FROM ubuntu:14.04

# File Author / Maintainer
MAINTAINER Tal Yarkoni

# Set all environment variables we'll need
ENV data_dir /data

# Add the application resources URL
RUN echo "deb http://archive.ubuntu.com/ubuntu/ $(lsb_release -sc) main universe" >> /etc/apt/sources.list

# Update the sources list
RUN apt-get update

# Install basic applications
RUN apt-get install -y --no-install-recommends tar git curl nano wget dialog net-tools build-essential

# install other non-Python packages: redis, node, MySQL, nginx
RUN apt-get -y --no-install-recommends install redis-server npm mysql-server nginx

# install coffeescript with Node
RUN npm install -g coffee-script

# Install Python and various packages
RUN apt-get -y --no-install-recommends install python python-dev python-distribute python-pip python-numpy python-scipy python-matplotlib ipython ipython-notebook python-pandas python-sympy python-nose python-mysqldb python-tk

WORKDIR /opt

# Clone github repo--temporary
RUN git clone https://github.com/PsychoinformaticsLab/neurosynth-web.git

# Get pip to download and install requirements:
RUN pip install -r neurosynth-web/requirements.txt

# Expose ports
EXPOSE 80

# Set the default directory where CMD will execute
WORKDIR /opt/neurosynth-web

# Copy the settings template
RUN cp nsweb/initializers/settings_template.py nsweb/initializers/settings.py

# Replace with ENV variables
RUN sed -i 's/\/root\/path\/to\/data/${data_dir}/g' nsweb/initializers/settings.py