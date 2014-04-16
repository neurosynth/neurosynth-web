from nsweb.core import add_blueprint
from flask import Blueprint, render_template, redirect, jsonify, url_for
from flask.json import jsonify
from nsweb.models.peaks import Peak
from nsweb.models import peaks

bp = Blueprint('locations',__name__,url_prefix='/locations')

@bp.route('/<string:val>/')
def show(val):
	x,y,z,radius = [int(i) for i in val.split('_')]
	return render_template('locations/show.html',radius=radius,x=x,y=y,z=z)

@bp.route('/')
def index():
	return redirect(url_for('locations.show',id='0_0_0_6'))

add_blueprint(bp)



