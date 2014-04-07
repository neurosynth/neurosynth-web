from flask import Blueprint, render_template, request
from nsweb.models import Study
from nsweb.core import apimanager, add_blueprint

bp = Blueprint('studies',__name__,url_prefix='/studies')

@bp.route('/')
def index():
    """Returns the studies page."""
    return render_template('studies/index.html.slim',studies=Study.query.count())

@bp.route('/<int:id>/')
def show(id):
    study = Study.query.get_or_404(id)
    viewer_settings = {
        'scale': 0.75,
        'images': [ { 
            'name': 'activations',
            'data': {
                'dims': [91, 109, 91],
                'peaks': [[p.x,p.y,p.z] for p in study.peaks]
            },
            'colorPalette': 'red'
        }],
        'options': { 'panzoomEnabled': 'false' },
    }
    return render_template('studies/show.html.slim', study=study, viewer_settings=viewer_settings)

# @bp.route('/download')
# gave up on this b/c issue is not image download I think?
# def download():
#     image = 'sadf'
#     response = make_response(image)
#     response.headers["Content-Disposition"] = "attachment; filename=asdf"
#     return response

add_blueprint(bp)

# Begin API stuff
def update_result(result, **kwargs):
    """ Rename frequency to feature in JSON. 
    Note: this makes the JSON look nice when requests come in at
    /studies/3000, but breaks the native functionality when requests 
    come in at /studies/3000/frequencies.
    """
    if 'frequencies' in result:
        result['features'] = result.pop('frequencies')
        for f in result['features']:
            f['frequency'] = round(f['frequency'], 3)

def datatables_preprocessor(search_params={}, **kwargs):
    """ For DataTables AJAX requests, we may need to change the search params. 
    """

    if 'sEcho' in request.args:
        # Add any filters we need...
        search_params['limit']  = int(request.args['iDisplayLength'])
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
        result['iTotalRecords'] = Study.query.count()
        # Workaround for datatables. it wants total results after query too, We can only provide a rough estimate.
        result['iTotalDisplayRecords'] = int(result.pop('num_results'))*int(result.pop('total_pages'))
        result.pop('page')
        result['aaData'] = [ [d['title'], d['authors'], d['journal'], d['year'], '<a href=http://www.ncbi.nlm.nih.gov/pubmed/{0}>{0}</a>'.format(d['pmid']) ] for d in result.pop('objects') ]
        
includes=['pmid',
        'title',
        'authors',
        'journal',
        'year',
        'peaks',
        'peaks.x',
        'peaks.y',
        'peaks.z',
        # 'frequencies',
        # 'frequencies.frequency',
        # 'frequencies.feature_id',
        'features',
        'features.feature'
        ]
add_blueprint(apimanager.create_api_blueprint(Study,
                                              methods=['GET'],
                                              collection_name='studies',
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
