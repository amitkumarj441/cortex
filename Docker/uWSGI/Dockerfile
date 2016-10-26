FROM debian

MAINTAINER Amit Kumar Jaiswal <amitkumarj441@gmail.com>

####### Build #######

# Make enviorment noninteractive
ENV DEBIAN_FRONTEND noninteractive

#Add and lunch the install script
ADD install.sh /tmp/install.sh
RUN chmod +x /tmp/install.sh && sleep 5 && /tmp/install.sh
ADD default.yml /opt/uwsgi/default.yml

# Set the working conditions
WORKDIR /opt/web
EXPOSE 9000
CMD  uwsgi --yaml /opt/uwsgi/default.yml
