#!/bin/bash
echo 'starting postgres'
/etc/init.d/postgresql start
sleep 5

sudo -u postgres createdb worldbrain
sudo -u postgres psql -c "CREATE USER cortex with PASSWORD 'cortex';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE worldbrain to cortex;"
sudo -u postgres psql -c "ALTER USER cortex CREATEDB;"

echo "**** Define env variable ****"

export DJANGO_SETTINGS_MODULE="worldbrain.settings.development"
export DJANGO_SECRET_KEY=0123456789abcdefghijklmnopqrstuvwyxz
export DATABASE_NAME=worldbrain
export DATABASE_USER=cortex
export DATABASE_PASSWORD=cortex
export ES_HOST=127.0.0.1:9200
export PGHOST=localhost

echo "**** Starting the server ****"

nohup python /cortex/manage.py migrate > migrate_output.log &
sleep 5
python /cortex/manage.py createsuperuser
python /cortex/manage.py runserver
