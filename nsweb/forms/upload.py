from werkzeug import secure_filename
from flask.ext.wtf import Form
from wtforms import FileField

class UploadForm(Form):
    image_file = FileField('Image file')