import imp
import subprocess
# from nsweb.initializers import settings
settings = imp.load_source('settings', 'nsweb/initializers/settings.py')

command = "curl https://opbeat.com/api/v1/organizations/%s/" \
    "apps/%s/releases/ -H \"Authorization: Bearer %s\"" \
    " -d rev=`git log -n 1 --pretty=format:%%H`" \
    " -d branch=`git rev-parse --abbrev-ref HEAD`" \
    " -d status=completed" % (settings.OPBEAT_ORGANIZATION_ID,
                              settings.OPBEAT_APP_ID,
                              settings.OPBEAT_SECRET_TOKEN)

print command
# subprocess.call(command.split(' '))
subprocess.Popen(command, stdout=subprocess.PIPE, shell=True).communicate()