#!/bin/sh

# Copy settings template to settings
cp nsweb/initializers/settings_template.py nsweb/initializers/settings.py

# Launch redis service
sudo service redis-server start

# Launch celery
sudo mkdir -p /var/log/celery
celery worker --app=nsweb.core:celery -c 1 --workdir=/code --logfile=/var/log/celery/dev.log &
bash