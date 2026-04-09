#!/bin/sh

celery worker --autoscale=4,1 --app=nsweb.core:celery --workdir=/code --time-limit=60 --logfile=/logs/celery.log
