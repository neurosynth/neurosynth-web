from flask import Blueprint, render_template
from . import route
from nsweb.models import Study

bp = Blueprint('home', __name__)

@route(bp, '/studies')
def index():
    """Returns the homepage."""
    img = random.choice(['emotion', 'pain', 'language', 'attention', 'memory', 'motor', 'reward', 'sensation'])
    image = Image.where(:name => "feature_#{img}_reverse").joins(:feature).select(['images.id', 'images.name', 'features.name', 'features.n_studies']).first
    news_items = [] #NewsItem.paginate(:page => params[:page], :per_page => 3).order('created_at DESC')
    return render_template('index.html.slim',studies=Study.query.all())

@route(bp, '/studies/<id>')
def show(id):
    return render_template('studies/show.html', study=Study.query.get_or_404(id))

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
# 
#     def show
#         cols_to_keep = [
#             'studies.title', 'studies.authors', 'studies.journal', 'studies.abstract', 
#             'studies.year', 'studies.id', 'studies.n_peaks', 'studies.n_tables', 
#             'studies.pmid', 'studies.doi', 'peaks.x', 'peaks.y', 'peaks.z', 'features.name',
#             'feature_tags.freq as loading'
#         ]
#         col = params[:id] =~ /^\d+$/ ? :id : :doi
#         @study = Study.where(col => params[:id]).includes([:peaks, :features]).first
#         respond_with(@study)
#     end
