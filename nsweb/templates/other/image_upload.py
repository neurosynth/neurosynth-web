# from flask import request
# 
# @app.route('/upload', methods=['GET', 'POST'])
# def upload_file():
#     if request.method == 'POST':
#         f = request.files['the_file']
#         f.save('/var/www/uploads/uploaded_file.txt')
# 
# '''
# forget this. Re-implementing flask-uploads. I looked at code and its doing exactly
#  what I am now and they have testing harness and safety stuff! Let's use that instead. 
# '''

'''
TODO: Weird import. wants me to use a nspkg.pth instead of just a normal import...or this type of import
'''

import os.path
from flask import Flask, redirect, request, render_template, url_for
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.storage import get_default_storage_class
from flask.ext.uploads import delete, init, save, Upload

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.config['DEFAULT_FILE_STORAGE'] = 'filesystem'
app.config['UPLOADS_FOLDER'] = os.path.realpath('.') + '/static/'
app.config['FILE_SYSTEM_STORAGE_FILE_VIEW'] = 'static'
init(SQLAlchemy(app), get_default_storage_class(app))


@app.route('/')
def index():
    """List the uploads."""
    uploads = Upload.query.all()
    return render_template('list.html', uploads=uploads)


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    """Upload a new file."""
    if request.method == 'POST':
        save(request.files['upload'])
        return redirect(url_for('index'))
    return render_template('upload.html')


@app.route('/delete/<int:id>', methods=['POST'])
def remove(id):
    """Delete an uploaded file."""
    upload = Upload.query.get_or_404(id)
    delete(upload)
    return redirect(url_for('index'))