#!/bin/sh

# Copy settings template to settings
cp nsweb/initializers/settings_template.py nsweb/initializers/settings.py
/usr/local/bin/gunicorn -w 2 -b :8000 nsweb.core:app --log-level debug