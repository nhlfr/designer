#!/bin/bash

set -e

pip install -U -e /opt/shmir

echo "Seting up database..."
# Sometimes psql returns TCP connection error, but it works when command is
# just repeated one time more.
# Probably it's a problem with container linking.
until psql -U postgres -h $DB_PORT_5432_TCP_ADDR < /opt/shmir/shmirdesignercreate.sql # &> /dev/null
do
    sleep 0.1
done
# psql -U postgres -h $DB_PORT_5432_TCP_ADDR < /opt/shmir/shmirdesignercreate.sql

shmir-db-manage upgrade
shmir-db-seed

echo "Running supervisor"

exec /usr/bin/supervisord -c /etc/supervisor/supervisord.conf
