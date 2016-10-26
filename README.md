[![Stories in Ready](https://badge.waffle.io/WorldBrain/cortex.png?label=ready&title=Ready)](https://waffle.io/WorldBrain/cortex) [![codecov](https://codecov.io/gh/WorldBrain/cortex/branch/master/graph/badge.svg)](https://codecov.io/gh/WorldBrain/cortex)

# cortex

`cortex` is the back-end server for the [webmarks](https://github.com/WorldBrain/webmarks) project.

It is a [django](https://www.djangoproject.com/) and [django-rest-framework](http://www.django-rest-framework.org/) powered application.

# Installation
Fork this repo and get a local copy with:

```
$ git clone https://github.com/<username>/cortex && cd $_
```

Please [create and activate virtualenv first] (http://docs.python-guide.org/en/latest/dev/virtualenvs/).

Before installing the dependencies, please install the following packages after updating the package index(```sudo apt-get update```):
```
sudo apt-get -y install python
sudo apt-get -y install build-essential
sudo apt-get -y install python-dev
sudo apt-get -y install libpq-dev
sudo apt-get -y install python-pip
sudo apt-get -y install libxml2-dev
sudo apt-get -y install libxslt1-dev
sudo apt-get -y install libldap2-dev
sudo apt-get -y install libsasl2-dev
sudo apt-get -y install libffi-dev
sudo apt-get -y install postgresql
sudo apt-get -y install postgresql-contrib
```

We use [pip-tools](https://github.com/nvie/pip-tools) and [pip](https://pip.pypa.io/en/stable/installing/) to manage our requirements:

```
$ pip install -r requirements/development.txt
```

Get a PostgreSQL database and a user up and running:

```
$ sudo -u postgres createdb worldbrain
$ sudo -u postgres psql
postgres=# CREATE USER cortex with PASSWORD 'cortex';
postgres=# GRANT ALL PRIVILEGES ON DATABASE worldbrain to cortex;
postgres=# ALTER USER cortex CREATEDB;
```

You'll then need to export a number of environment variables.

```
export DJANGO_SETTINGS_MODULE="worldbrain.settings.development"
export DJANGO_SECRET_KEY=0123456789abcdefghijklmnopqrstuvwyxz
export DATABASE_NAME=worldbrain
export DATABASE_USER=cortex
export DATABASE_PASSWORD=cortex
export ES_HOST=127.0.0.1:9200
export PGHOST=localhost
```

After that, you can then run:

```
$ python manage.py migrate
$ python manage.py createsuperuser
$ python manage.py runserver
```

When working on _Mac OS_, some problems with **psycopg2**, **libcrypto.1.0.0.dylib**, and **libssl.1.0.0.dylib** can occur due to 
the installation path of **PostrgreSQL**. To avoid them, add the _bin_ 
and the _lib_ path of **PostgreSQL** to _PATH_ 
(e.g. _PATH=$PATH:/Library/PostgreSQL/9.5/bin:/Library/PostgreSQL/9.5/lib:_).

If you still have trouble with **psycopg2**, **libcrypto.1.0.0.dylib**, and **libssl.1.0.0.dylib**, the reason could 
probably be the missing symlinks ot the libraries. Set the links by running:

```
$ sudo ln -s /your/PostgreSQL/installation/path/lib/libssl.1.0.0.dylib /usr/local/lib
$ sudo ln -s /your/PostgreSQL/installation/path/lib/libcrypto.1.0.0.dylib /usr/local/lib
```

Please note, that due to System Integrity Protection, you can not write into _/usr/lib_ on _Mac OS X El Capitan_ and up.

If after running the _python manage.py runserver_ command the app can not connect to the server
via Unix domain socket, you have to:

```
export PGHOST=localhost
```
In case you face an error like **FATAL:  password authentication failed for user "cortex"**, try the follwing commands:
```
$ sudo -u postgres psql worldbrain
worldbrain=# ALTER USER cortex PASSWORD 'cortex'
```
You also can use the starter script provided:

```
./starter_script.sh
```

to start the development server.


You can also setup the dev env using docker

```
docker pull worldbrain/cortex
docker run -it --net=host --name=cortex worldbrain/cortex
```

Happy hacking!

# Testing
We are using [py.test][pytest] for our testing. You can run them with:

```
$ py.test worldbrain           # test runner
$ ptw worldbrain -- --testmon  # test watcher
```
