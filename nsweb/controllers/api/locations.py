from nsweb.controllers.api import bp
from flask import request, jsonify, url_for
from nsweb.models import Location, Peak

# @bp.route('/locations/')
# def get_location_list():
#     locations = Location.query.all()
#     data = [{'x': l.x, 'y': l.y, 'z': l.z} for l in locations]
#     return jsonify(data=data)

@bp.route('/locations/<string:val>/')
def location_api(val):
    args = [int(i) for i in val.split('_')]
    if len(args) == 3: args.append(10)
    x, y, z, radius = args

    ### PEAKS ###
    # Limit search to 20 mm to keep things fast
    if radius > 20: radius = 20
    points = Peak.closestPeaks(radius,x,y,z)
    points = points.group_by(Peak.pmid) #prevents duplicate studies
    points = points.add_columns(sqlalchemy.func.count(Peak.id)) #counts duplicate peaks

    ### IMAGES ###
    location = Location.query.filter_by(x=x, y=y, z=z).first()
    images = [] if location is None else location.images
    images = [{'label': i.label, 'id': i.id} for i in images if i.display]

    if 'sEcho' in request.args:
        data = []
        for p in points:
            s = p[0].study
            link = '<a href={0}>{1}</a>'.format(url_for('studies.show',val=s.pmid),s.title)
            data.append([link, s.authors, s.journal,p[1]])
        data = jsonify(aaData=data)
    else:
        data = {
            'studies': [{'pmid':p[0].study.pmid,'peaks':p[1] } for p in points],
            'images': images
        }
        data = jsonify(data=data)
    return data