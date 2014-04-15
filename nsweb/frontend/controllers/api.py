from nsweb.core import add_blueprint
from flask import Blueprint, redirect, jsonify, url_for, request
from nsweb.models import *

bp = Blueprint('apis',__name__,url_prefix='/api')


# Begin server side APIs 
@bp.route('/studies/')
def studies_server_side_api():
    results_per_page = int(request.args['iDisplayLength'])
    offset = int(request.args['iDisplayStart'])
    order_by = '{0} {1}'.format(['title','authors','journal','year','pmid'][int(request.args['iSortCol_0'])],str(request.args['sSortDir_0']))
    search = str(request.args['sSearch']).strip()
    data = Study.query
    if search:
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
    order_by = '{0} {1}'.format(['feature','num_studies','num_activations'][int(request.args['iSortCol_0'])],str(request.args['sSortDir_0']))
    search = str(request.args['sSearch']).strip()
    data = Feature.query
    if search:
        search = '%{}%'.format(search)
        data = data.filter( Feature.feature.like( search ) | Feature.num_studies.like( search ) | Feature.num_activations.like( search ) )
    data=data.order_by(order_by)
    data=data.paginate(page=offset/results_per_page, per_page=results_per_page, error_out=False)
    result = {}
    result['sEcho'] = int(request.args['sEcho']) # for security
    result['iTotalRecords'] = Feature.query.count()
    result['iTotalDisplayRecords'] = data.total
    result['aaData'] = [ ['<a href={0}>{1}</a>'.format(url_for('features.show',val=d.id),d.feature),
                            d.num_studies,
                            d.num_activations,
                            ] for d in data.items ]
    result=jsonify(**result)
    return result

# Begin client side APIs 
@bp.route('/studies/<int:val>/')
def studies_api(val):
    data=Study.query.get_or_404(val)
    data = [ ['<a href={0}>{1}</a>'.format(url_for('features.show',val=f.feature_id),f.feature.feature),
              round(f.frequency,3),
              ] for f in data.frequencies]
    data=jsonify(aaData=data)
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
    data = Feature.query.get_or_404(val)
    data = [ ['<a href={0}>{1}</a>'.format(url_for('studies.show',val=f.pmid),f.study.title),
              f.study.authors,
              f.study.journal,
              round(f.frequency,3),
              ] for f in data.frequencies]
    data=jsonify(aaData=data)
    return data

@bp.route('/locations/<string:val>')
def locations_api(val):
    x,y,z,radius = [int(i) for i in val.split('_')]
    points = Peak.closestPeaks(radius,x,y,z)
    data = [ [p.study.title, p.study.authors, p.study.journal] for p in points]
    return jsonify(aaData=data)

add_blueprint(bp)
