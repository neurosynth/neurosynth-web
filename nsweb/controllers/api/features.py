from nsweb.controllers.api import bp
from flask import request, jsonify, url_for
from nsweb.models import Feature

@bp.route('/features/')
def get_feature_list():
    args = request.get_json()
    results_per_page = int(args['length'])
    offset = int(args['start'])
    order_by = '{0} {1}'.format(['name','num_studies','num_activations'][int(request.args['order[0][column]'])],str(request.args['order[0][dir]']))
    search = str(request.args['search[value]']).strip()
    data = Feature.query
    if search: #No empty search on my watch
        search = '%{}%'.format(search)
        data = data.filter( Feature.name.like( search ) | Feature.num_studies.like( search ) | Feature.num_activations.like( search ) )
    data=data.order_by(order_by)
    data=data.paginate(page=(offset/results_per_page)+1, per_page=results_per_page, error_out=False)
    result = {}
    result['draw'] = int(request.args['draw']) # for security
    result['recordsTotal'] = Feature.query.count()
    result['recordsFiltered'] = data.total
    result['data'] = [ ['<a href={0}>{1}</a>'.format(url_for('features.show',val=d.name),d.name),
                            d.num_studies,
                            d.num_activations,
                            ] for d in data.items ]
    result=jsonify(**result)
    return result

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