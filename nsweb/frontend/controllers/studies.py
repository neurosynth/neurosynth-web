from flask import Blueprint, render_template, request, make_response
from nsweb.models import Study
from nsweb.core import apimanager, add_blueprint

bp = Blueprint('home',__name__,url_prefix='/studies')

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
        'settings': { 'panzoomEnabled': 'false' },
    }
    return render_template('studies/show.html.slim', study=study, viewer_settings=viewer_settings)

@bp.route('/download')
# gave up on this b/c issue is not image download I think?
def download():
    image = 'sadf'
    response = make_response(image)
    response.headers["Content-Disposition"] = "attachment; filename=asdf"
    return response

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
        pass

def datatables_postprocessor(result, **kwargs):
    """ A wrapper for DataTables requests. Just takes the JSON object to be 
    returned and adds the fields DataTables is expecting. This should probably be 
    made a universal postprocessor and applied to all API requests that have a 
    'datatables' key in the request arguments list. """
    if 'sEcho' in request.args:
        result['iTotalRecords'] = Study.query.count()  # Get the number of total records from DB
        result['iTotalDisplayRecords'] = result.pop('num_results')
        result['aaData'] = result.pop('objects')
        result['sEcho'] = int(request.args['sEcho'])  # for security
        # ...and so on for anything else we need

def datatables_preprocessor(search_params=None, **kwargs):
    """ For DataTables AJAX requests, we may need to change the search params. 
    """
    # if 'sEcho' in request.args:
    #     # Add any filters we need...
    #     search_params = {
    #         'filters': {
    #             'offset': request.args['iDisplayStart']
    #         }
    #     }
        # Convert the DataTables query parameters into what flask-restless wants
        # if 'iDisplayStart' in request.args:

        

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
