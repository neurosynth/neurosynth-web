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
        'options': { 'panzoomEnabled': 'false' },
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

def datatables_postprocessor(result, **kwargs):
    from itertools import islice
    """ A wrapper for DataTables requests. Just takes the JSON object to be 
    returned and adds the fields DataTables is expecting. This should probably be 
    made a universal postprocessor and applied to all API requests that have a 
    'datatables' key in the request arguments list. """
    if 'sEcho' in request.args:
        result['sEcho'] = int(request.args['sEcho']) # for security
        result['iTotalRecords'] = Study.query.count()  # Get the number of total records from DB
        result['iTotalDisplayRecords'] = result.pop('num_results')
        result.pop('total_pages')
        result.pop('page')
        data = result.pop('objects')
        data = [ [d['title'], d['authors'], d['journal'], d['year'], d['pmid']] for d in data ]
        result['aaData'] = data
        
        # ...and so on for anything else we need

#     def index
#         # @studies = Study.all
#         # @num_studies = Study.count
#         cols = ['title', 'authors', 'journal', 'year', 'pmid']
#         param_sort_col = params[:iSortCol_0].nil? ? (params[:sort] || 'pmid') : cols[params[:iSortCol_0].to_i]
#         param_sort_ord = (params[:sSortDir_0] || params[:order] || 'ASC')
#         param_search = (params[:sSearch] || params[:q] || '')
#         param_start = (params[:iDisplayStart] || params[:start] || 0).to_i
#         param_per = (params[:iDisplayLength] || params[:perPage] || 20).to_i
#         param_per = [param_per, 100].min   # Display max 100 records
#         order = "#{param_sort_col} #{param_sort_ord}"
#         count = Study.count
#         studies = Study.scoped
#         if !param_search.empty?
#             studies = studies.where("MATCH(title, authors, journal) AGAINST ('*#{param_search}*' IN BOOLEAN MODE)")
#             itdr = studies.size
#         else
#             itdr = count
#         end
#         studies = studies.order(order).limit(param_per).offset(param_start).select(['id'] + cols)
#         @data = {
#             :studies => studies,
#             :iTotalRecords => count,
#             :iTotalDisplayRecords => itdr,
#             :sEcho => params[:sEcho]
#         }
#         respond_with(@data)
#     end

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
