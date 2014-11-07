
# neurosynth-web

This is the stuff that runs [neurosynth.org](http://neurosynth.org).

## Installation

Installation can be a rather cumbersome process. There are a large number of dependencies, some of which are platform-specific. To get a working development app, something like the following steps should work:

1. Create a new virtual-env to house all the Python dependencies.
2. Install the [Neurosynth](http://github.com/neurosynth/neurosynth) package and its dependencies, as well as core computational/plotting packages:

	pip install numpy scipy matplotlib pandas seaborn scikit-learn ply neurosynth

3. Install node and coffeescript
4. Install Flask and various other packages (see requirements.txt):

	pip install SQLalchemy Flask simplejson jinja2 cssmin webassets pyscss Flask-Assets Flask-Babel Flask-Cake Flask-Mail Flask-Migrate Flask-Script Flask-SQLAlchemy Flask-User Flask-WTF

5. Install MySQL or MariaDB and a Python MySQL adapter (PyMySQL or MySQL-Python)
6. Optional: Install and configure uwsgi. Copy or rename deploy/deploy-dev-template.ini to deploy/deploy-dev.ini. Modify settings as needed. Alternatively, you can just run python run_server.py to rely on the built-in server for local development.
7. Optional: install and configure nginx or Apache to point to the development app. This isn't covered here. Alternatively, you can just run python run_server.py to rely on the built-in server for local development.
8. Install redis and celery
9. Copy or rename nsweb/initializers/settings-template.py to nsweb/initializers/settings.py. Change the root data path at the top to a writeable directory, and edit the MySQL settings as needed. Make sure the user exists in MySQL and has write privileges to the correct database(s).
10. Download the latest Neurosynth data files from  [https://github.com/neurosynth/neurosynth-data/blob/master/current_data.tar.gz](https://github.com/neurosynth/neurosynth-data/blob/master/current_data.tar.gz). Extract the .txt files and put the in the assets/ folders below the data root specified in settings.py.
11. Optional: obtain ~300GB of functional connectivity images from Thomas Yeo and put them in an 'fcmri' folder under settings.IMAGE_DIR.
12. Edit setup_database.py if desired. For rapid development/prototyping, set PROTOTYPE=True in settings.py. This will only populate the DB with a small fraction of the data rather than using all of it.
13. Run python setup_database.py. Wait somewhere between a few minutes and a day or two. Check MySQL database to make sure that tables have stuff in them.
14. Launch the web server and navigate to the site. Make sure everything works. It probably won't. Fix whatever's broken. Then try again. Rinse and repeat.

