from flask import Blueprint, render_template, request, make_response
from nsweb.models import Feature
from nsweb.core import apimanager, add_blueprint

bp = Blueprint('home',__name__,url_prefix='/features')
 
@bp.route('/')
def index():
    return render_template('features/index.html', features=Feature.query.count())
 
# @features.route('/<id>')
# def show(id):
#     # return features.root_path
#     if re.match('\d+$', id):
#         feature = Feature.query.get_or_404(id)
#     else:
#         feature = Feature.query.filter_by(feature=id).first_or_404()
#     return render_template('features/show.html', feature=feature)
#  
# add_blueprint(features)


# Begin API stuff
def find_feature(instance_id, **kwargs):
    """ If the passed ID isn't numeric, assume it's a feature name,
    and retrieve the corresponding numeric ID. 
    DOES NOT WORK BECAUSE CANNOT OVERWRITE instance_id. """
    if not re.match('\d+$', instance_id):
        instance_id = Feature.query.filter_by(feature=instance_id).first().id
    pass

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
        search_params['limit'] = request.args['iDisplayLength']
        search_params['offset'] = request.args['iDisplayStart']
                #'order_by': request.args['']
#                 'filters' : 
        # Convert the DataTables query parameters into what flask-restless wants
        # if 'iDisplayStart' in request.args:

def datatables_postprocessor(result, **kwargs):
    """ A wrapper for DataTables requests. Just takes the JSON object to be 
    returned and adds the fields DataTables is expecting. This should probably be 
    made a universal postprocessor and applied to all API requests that have a 
    'datatables' key in the request arguments list. """
    if 'sEcho' in request.args:
        result['sEcho'] = int(request.args['sEcho']) # for security
        result['iTotalRecords'] = Feature.query.count()  # Get the number of total records from DB
        result['iTotalDisplayRecords'] = result.pop('num_results')
        result.pop('total_pages')
        result.pop('page')
        data = result.pop('objects')
        data = [ [d['name'], 1] for d in data ] # TODO: 1 is supposed to be frequency. I don't want to rebuild or play with models yet. That can be done after page is working
        result['aaData'] = data
        
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
