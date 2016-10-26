# Description : Docker file for building the image for cortex
# Version : 1.0
# Date : 3 October 2016
# Author : Vigneshwer

FROM ubuntu
MAINTAINER Vigneshwer

# Replace sh with bash
RUN rm /bin/sh && ln -s /bin/bash /bin/sh

# Set root password for the image
RUN echo 'root:root' | chpasswd

# Installing git
RUN apt-get update &&\
	apt-get -y install git

# Installing python, python-pip and necessary libraries for the python packages
RUN apt-get update &&\
	apt-get -y install python &&\
   	apt-get -y install build-essential &&\
	apt-get -y install python-dev &&\
	apt-get -y install libpq-dev &&\
	apt-get -y install python-pip &&\
	apt-get install -y libxml2-dev &&\
	apt-get install -y libxslt1-dev &&\
	apt-get install -y libldap2-dev &&\
	apt-get install -y libsasl2-dev &&\
	apt-get install -y libffi-dev &&\
	apt-get install -y postgresql &&\
	apt-get install -y postgresql-contrib

# Clone the cortex project and install the requirments
RUN git clone https://github.com/WorldBrain/cortex.git &&\
	cd /cortex &&\
	pip install --upgrade pip &&\
	pip install -r ./requirements/development.txt

RUN apt-get install sudo

#setup postgres
RUN echo "host all  all    0.0.0.0/0  md5" >> /etc/postgresql/9.5/main/pg_hba.conf
RUN echo "listen_addresses='*'" >> /etc/postgresql/9.5/main/postgresql.conf

COPY ./startup.sh /cortex/

EXPOSE 8000 5432 9200

ENTRYPOINT /bin/bash /cortex/startup.sh
