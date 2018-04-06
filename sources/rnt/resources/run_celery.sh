#!/bin/sh

cd /code

# wait for RabbitMQ server to start
sleep 10

# run Celery worker for our project myproject with Celery configuration stored in Celeryconf
su -m myuser -c "celery worker -A rnt.celeryconf -Q default -n default@%h"
#celery worker -A rnt.celeryconf -Q default -n default@%h