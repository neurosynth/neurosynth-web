from nsweb.core import add_blueprint, db
from flask import Blueprint, redirect, jsonify, url_for, request
from nsweb.models import *
from flask_sqlalchemy import sqlalchemy
bp = Blueprint('apis',__name__,url_prefix='/api')


### NOTE: THIS API IS BEING GRADUALLY PHASED OUT IN FAVOR OF METHODS IN THE 
# MODEL SPECIFIC CONTROLLER MODULES. ###

# Begin server side APIs 
@bp.route('/studies/')
def studies_server_side_api():
    data = Study.query
    results_per_page = int(request.args['iDisplayLength'])
    offset = int(request.args['iDisplayStart'])
    order_by = '{0} {1}'.format(['title','authors','journal','year','pmid'][int(request.args['iSortCol_0'])],str(request.args['sSortDir_0']))
    search = str(request.args['sSearch']).strip()
    if search:#No empty search on my watch
        search = '%{}%'.format(search)
        data=data.filter( Study.title.like( search ) | Study.authors.like( search ) | Study.journal.like( search ) | Study.year.like( search ) | Study.pmid.like(search) )
    data=data.order_by(order_by)
    data=data.paginate(page=offset/results_per_page, per_page=results_per_page, error_out=False)
    result = {}
    result['sEcho'] = int(request.args['sEcho']) # for security
    result['iTotalRecords'] = Study.query.count()
    result['iTotalDisplayRecords'] = data.total
    result['aaData'] = [ ['<a href={0}>{1}</a>'.format(url_for('studies.show',val=d.pmid),d.title),
                          d.authors,
                          d.journal,
                          d.year,
                          '<a href=http://www.ncbi.nlm.nih.gov/pubmed/{0}>{0}</a>'.format(d.pmid) ] for d in data.items ]
    result=jsonify(**result)
    return result

@bp.route('/features/')
def features_server_side_api():
    results_per_page = int(request.args['iDisplayLength'])
    offset = int(request.args['iDisplayStart'])
    order_by = '{0} {1}'.format(['name','num_studies','num_activations'][int(request.args['iSortCol_0'])],str(request.args['sSortDir_0']))
    search = str(request.args['sSearch']).strip()
    data = Feature.query
    if search: #No empty search on my watch
        search = '%{}%'.format(search)
        data = data.filter( Feature.name.like( search ) | Feature.num_studies.like( search ) | Feature.num_activations.like( search ) )
    data=data.order_by(order_by)
    data=data.paginate(page=offset/results_per_page, per_page=results_per_page, error_out=False)
    result = {}
    result['sEcho'] = int(request.args['sEcho']) # for security
    result['iTotalRecords'] = Feature.query.count()
    result['iTotalDisplayRecords'] = data.total
    result['aaData'] = [ ['<a href={0}>{1}</a>'.format(url_for('features.show',val=d.name),d.name),
                            d.num_studies,
                            d.num_activations,
                            ] for d in data.items ]
    result=jsonify(**result)
    return result

# Begin client side APIs 
@bp.route('/studies/features/<int:val>/')
def studies_features_api(val):
    data=Study.query.get(val)
#     data=Frequency.query.filter_by(pmid=int(val))#attempted optimization. Join causes slower performance however
    data = [ ['<a href={0}>{1}</a>'.format(url_for('features.show',val=f.feature_id), f.feature.name),
              round(f.frequency,3),
              ] for f in data.frequencies]
    data=jsonify(aaData=data)
    return data

@bp.route('/studies/peaks/<int:val>/')
def studies_peaks_api(val):
    data=Study.query.get(val)
#     data=Peak.query.filter_by(pmid=int(val))#attempted optimization. Join causes slower performance however
    data=[ [p.table,p.x,p.y,p.z] for p in data.peaks]
#     data=Peak.query.filter_by(pmid=int(val)).with_entities(Peak.x,Peak.y,Peak.z).all() #attempted optimization.
    data=jsonify(data=data)
    return data

@bp.route('/features/<string:name>/')
def find_api_feature(name):
    """ If the passed val isn't numeric, assume it's a feature name,
    and retrieve the corresponding numeric ID. 
    """
    val = Feature.query.filter_by(feature=name).first().id
    return redirect(url_for('features.api',id=val))

@bp.route('/features/<int:val>/')
def features_api(val):
    data = Feature.query.get(val)
#     data=Frequency.query.filter_by(feature_id=int(val))#attempted optimization. Join causes slower performance however
    data = [ ['<a href={0}>{1}</a>'.format(url_for('studies.show',val=f.pmid),f.study.title),
              f.study.authors,
              f.study.journal,
              round(f.frequency,3),
              ] for f in data.frequencies]
    data=jsonify(aaData=data)
    return data

@bp.route('/locations/')
def location_list_api():
    locations = Location.query.all()
    data = [{'x': l.x, 'y': l.y, 'z': l.z} for l in locations]
    return jsonify(data=data)

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
    
add_blueprint(bp)
