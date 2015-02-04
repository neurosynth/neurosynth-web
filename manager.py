from nsweb.core import app, db, create_app
from flask.ext.script import Manager
from flask import url_for
from flask.ext.migrate import Migrate, MigrateCommand
from nsweb.models import *

create_app(app)
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

# Found @ http://stackoverflow.com/questions/13317536/get-a-list-of-all-routes-defined-in-the-app
@manager.command
def list_routes():
    import urllib

    output = []
    for rule in app.url_map.iter_rules():
        methods = ','.join(rule.methods)
        line = urllib.unquote("{:50s} {:20s} {}".format(rule.endpoint, methods, rule))
        output.append(line)

    for line in sorted(output):
        print(line)

if __name__ == '__main__':
    manager.run()