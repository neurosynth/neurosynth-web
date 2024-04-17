# Set the base image to Ubuntu
FROM ubuntu:18.04

# File Author / Maintainer
MAINTAINER Tal Yarkoni

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# Update the sources list and install basic applications
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    apt-get install -y --no-install-recommends tar git curl nano wget dialog net-tools build-essential sudo

# Install other non-Python packages: node, nginx, etc.
RUN DEBIAN_FRONTEND=noninteractive apt-get -y --no-install-recommends install tzdata
RUN apt-get -y --no-install-recommends install redis-server nodejs npm nginx

# Dependencies for the various python libs (might be needed for certain Conda packages)
RUN apt-get install -y gfortran libopenblas-dev liblapack-dev pkg-config libjpeg8-dev libfreetype6-dev libpng-dev postgresql postgresql-contrib libpq-dev libxml2-dev libxslt-dev

# Install coffeescript with Node
RUN npm config set registry http://registry.npmjs.org/ && \
    npm config set strict-ssl false && \
    npm install -g coffeescript

# Install Miniconda
ENV PATH /opt/conda/bin:$PATH
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh
RUN bash /tmp/miniconda.sh -b -u -p /opt/conda
RUN conda update -n base -c defaults conda
RUN conda install -y python==3.9
RUN conda install -y numpy pandas scipy
RUN conda install -y scikit-learn=0.24
RUN conda install -c conda-forge uwsgi 
# Copy the code directory to install Python packages etc.
COPY . /tmp/code

WORKDIR /tmp/code

# Install all Python packages with conda or pip
RUN pip install setuptools==58
RUN pip install pip==9.0.3
RUN pip install pybind11
RUN pip install cppy
RUN git clone https://github.com/neurosynth/neurosynth.git
RUN cd neurosynth & pip install .
RUN cd ../
RUN pip install -r requirements.txt
