#!/bin/sh

celery worker --autoscale=10,3 --app=nsweb.core:celery --workdir=/code --time-limit=60 --logfile=/logs/celery.log
