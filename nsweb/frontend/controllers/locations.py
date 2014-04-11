from nsweb.core import add_blueprint
from nsweb.models import Location
from flask import Blueprint, render_template, redirect, jsonify, url_for
from flask.json import jsonify

bp = Blueprint('locations',__name__,url_prefix='/locations')

def translateCoords(id):
	'''
	Translates coords from x_y_z to x,y,z
	'''
	return [int(i) for i in id.split('_')]

@bp.route('/')
def index():
	return redirect(url_for('locations.show',id='0_0_0'))

@bp.route('/<string:id>')
def show(id):
	x,y,z = translateCoords(id)
	radius=6
	peaks = Location.closestPeaks(radius,x,y,z)
	return render_template('locations/show.html', radius=radius, xyz=[x,y,z])

@bp.route('/api/<string:id>')
def api(id):
	x,y,z = translateCoords(id)
	peaks = Location.closestPeaks(6,x,y,z)
	data = [ [p.study.title, p.study.authors, p.study.journal] for p in peaks]
	return jsonify(aadata=data)

add_blueprint(bp)



