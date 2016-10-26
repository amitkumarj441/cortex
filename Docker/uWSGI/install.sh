#!bin/bash

# uWSGI Install script

# VARIABLES

BUILD_DIR="/tmp/uwsgi"

# ENVIRONMENT

set +e

# EXECUTION

echo "> Go to build directory"
mkdir "${BUILD_DIR}"
cd "${BUILD_DIR}"

echo "> Update the system"
apt-get update -y
apt-get upgrade -y

echo "> Install the build dependencies"
apt-get -y install \
	build-essential \
	python3-dev \
	python3-pip \
	python3-psycopg2 \
	curl
apt-get clean
apt-get install -U pip

echo " >Install uwsgi"
pip3 install -U uwsgi
mkdir -p /opt/uwsgi/conf.d

echo " > Install django"
pip3 install -U django

echo " > Cleanup"
rm -fr "${BUILD_DIR}"
