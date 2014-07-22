from nsweb.core import app, db, create_app
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
from nsweb.models import *

create_app(app)
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()