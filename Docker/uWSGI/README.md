# uWSGI

This docker image runs uwsgi on port 9000.
Django is included.
The default config file used is located in /opt/uwsgi/default.yml
It includes any .yml config files located in to /opt/uwsgi/conf.d directory.
While the config file does include the vbasic configuration, it is unaware of your application.
You should give it the filloing two enviormental variables:

* UWSGI_CHDIR - /cortex
* UWSGI_WSGI_FILE - [wsgi.py](https://github.com/WorldBrain/cortex/blob/master/worldbrain/wsgi.py)

## Usage

You can then run this container like this:
```
docker run -d \
	-v <path to your app>:/cortex \
	-e UWSGI_CHDIR=/cortex \
	-e UWSGI_WSGI_FILE=<https://github.com/WorldBrain/cortex/blob/master/worldbrain/wsgi.py> \
	--name uwsgi-container \
	cortex/uwsgi
```
You can then link a front web server to it, using it's exposed port 9000 as an upstream.
