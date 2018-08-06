#!/bin/bash

# Copy settings template to settings if latter doesn't exist
[ ! -e nsweb/initializers/settings.py ] && cp nsweb/initializers/settings_template.py nsweb/initializers/settings.py

# Run setup script if pickled dataset doesn't exist
[ ! -d /data/assets/neurosynth_dataset.pkl ] && python3 /code/setup_database.py

# Start up gunicorn
/usr/local/bin/gunicorn -w 2 -b :8000 runserver:app --reload --log-level debug
