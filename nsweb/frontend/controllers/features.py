from flask import Blueprint, render_template, request, redirect, url_for
from nsweb.models import Feature
from nsweb.core import apimanager, add_blueprint

bp = Blueprint('features',__name__,url_prefix='/features')
 
@bp.route('/')
def index():
    return render_template('features/index.html.slim', features=Feature.query.all())
 
@bp.route('/<int:id>/')
def show(id):
    # return features.root_path
    feature = Feature.query.get_or_404(id)
    return render_template('features/show.html.slim', frequencies=feature.frequencies, feature=feature.feature)

@bp.route('/<string:name>/')
def find_feature(name):
    """ If the passed ID isn't numeric, assume it's a feature name,
    and retrieve the corresponding numeric ID. 
    DOES NOT WORK BECAUSE CANNOT OVERWRITE instance_id. """
    id = Feature.query.filter_by(feature=name).first().id
    return redirect(url_for('features/'+str(id)))

add_blueprint(bp)


# Begin API stuff
def update_result(result, **kwargs):
    """ Rename frequency to study in JSON. """
    if 'frequencies' in result:
        result['studies'] = result.pop('frequencies')
        for s in result['studies']:
            s['frequency'] = round(s['frequency'], 3)

def datatables_preprocessor(search_params={}, **kwargs): #TODO: move to init or a helper. This is same everwhere...
    """ For DataTables AJAX requests, we may need to change the search params. 
    """

    if 'sEcho' in request.args:
        # Add any filters we need...
        search_params['results_per_page'] = int(request.args['iDisplayLength'])
        search_params['offset'] = int(request.args['iDisplayStart'])

        #Yea... this is a list of dictionary... Flask-restless has an undocumented python 2.5 workaround hack that breaks documented functionality. This is the workaround for the workaround. -_-
        search_params['order_by'] = [{
                                      'field': ['title','authors','journal','year','pmid'][int(request.args['iSortCol_0'])] ,
                                      'direction': str(request.args['sSortDir_0'])
                                      }]
        search_params['filters'] = [
                                    {'name': 'title', 'op': 'like', 'val': '%'+str(request.args['sSearch'])+'%'},
                                    {'name': 'authors', 'op': 'like', 'val': '%'+str(request.args['sSearch'])+'%'},
                                    {'name': 'journal', 'op': 'like', 'val': '%'+str(request.args['sSearch'])+'%'},
                                    {'name': 'loading', 'op': 'eq', 'val': str(request.args['sSearch'])+'%'},
                                    {'name': 'year', 'op': 'eq', 'val': str(request.args['sSearch'])+'%'},
                                    {'name': 'pmid', 'op': 'eq', 'val': str(request.args['sSearch'])+'%'},
                                   ]
        search_params['disjunction'] = True

def datatables_postprocessor(result, **kwargs):
    """ A wrapper for DataTables requests. Just takes the JSON object to be 
    returned and adds the fields DataTables is expecting. This should probably be 
    made a universal postprocessor and applied to all API requests that have a 
    'datatables' key in the request arguments list. """
    if 'sEcho' in request.args:
        result['sEcho'] = int(request.args['sEcho']) # for security
        # Get the number of total records from DB
        result['iTotalRecords'] = Feature.query.count()
        # Workaround for datatables. it wants total results after query too, We can only provide a rough estimate.
        result['iTotalDisplayRecords'] = result.pop('num_results')
        result.pop('page')
        result.pop('total_pages')
        result['aaData'] = [ ['<a href=http://www.ncbi.nlm.nih.gov/pubmed/{0}>{1}</a>'.format(d['pmid'],d['title']),
                            d['authors'],
                            d['frequency'],
                            d['journal'],
                            d['year'],
                            ] for d in result.pop('objects') ]

#db columns
includes=['id',
        'feature',
        'num_studies',
        'num_activations',
        'images',
        'images.stat',
        'images.feature_id',
        'images.image_file',
        'images.label',
        'studies',
        'studies.pmid'
]
add_blueprint(apimanager.create_api_blueprint(Feature,
                                            methods=['GET'],
                                            collection_name='features',
                                            results_per_page=20,
                                            max_results_per_page=100,
                                            include_columns=includes,
                                              postprocessors={
                                                  'GET_SINGLE': [update_result],
                                                  'GET_MANY': [datatables_postprocessor]
                                              },
                                              preprocessors={
                                                  'GET_MANY': [datatables_preprocessor]
                                              }))
