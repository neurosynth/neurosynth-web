from nsweb.core import add_blueprint
from flask import Blueprint, render_template, redirect, jsonify, url_for
from flask.json import jsonify
from nsweb.models.peaks import Peak
from nsweb.models import peaks

bp = Blueprint('locations',__name__,url_prefix='/locations')

@bp.route('/<string:id>')
def show(id):
	x,y,z,radius = [int(i) for i in id.split('_')]
	points = Peak.closestPeaks(radius,x,y,z)
	return render_template('locations/show.html', radius=radius, xyz=[x,y,z])

@bp.route('/')
def index():
	return redirect(url_for('locations.show',id='0_0_0_6'))

add_blueprint(bp)



