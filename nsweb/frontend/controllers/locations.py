from nsweb.core import add_blueprint
from flask import Blueprint, render_template, redirect, url_for
from nsweb.models.locations import Location

bp = Blueprint('locations',__name__,url_prefix='/locations')

@bp.route('/<string:val>/')
def show(val):
    x,y,z,radius = [int(i) for i in val.split('_')]
    location = Location.Query.filter_by(x=x,y=y,z=z)
    images=''
    for i in location.images:
#        if i.visible:
        funcconn=i.label.find('funcconn')
        description = "This image displays resting-state functional connectivity for the seed region in a sample of 1,000 subjects. Image provided courtesy of Yeo, Buckner and colleagues. For details, see <a href='http://jn.physiology.org/content/106/3/1125.long'>Yeo et al (2011).</a>" if funcconn else 'This image displays regions coactivated with the seed region across all studies in the Neurosynth database. It represents meta-analytic coactivation rather than time series-based connectivity.'
        images+= '{{"name":"{0}","id":{1},"download":"/images/{1}","intent":"{2}","visible":{3},"colorPalette":{4}, "description":{5}},'.format(i.name,
                                                                                                                          i.id,
                                                                                                                          (i.stat + ' :').capitalize(),
                                                                                                                          'true' if funcconn else'false',
                                                                                                                          '"red","positiveThreshold" = 0.3,"negativeThreshold" = -0.3' if funcconn else '"yellow"',
                                                                                                                          description)
    #images = [{"name":"Neurosynth coactivation","id":103153,"download":"/images/103153/download","url":"/images/103153/download","intent":"Z-score:","colorPalette":"yellow","visible":false,"description":"This image displays regions coactivated with the seed region across all studies in the Neurosynth database. It represents meta-analytic coactivation rather than time series-based connectivity."},{"name":"Functional connectivity","id":103154,"download":"/images/103154/download","url":"/images/103154/download","intent":"Correlation (r):","colorPalette":"red","positiveThreshold":0.3,"negativeThreshold":-0.3,"description":"This image displays resting-state functional connectivity for the seed region in a sample of 1,000 subjects. Image provided courtesy of Yeo, Buckner and colleagues. For details, see <a href='http://jn.physiology.org/content/106/3/1125.long'>Yeo et al (2011).</a>"}]
    return render_template('locations/index.html.slim',radius=radius,x=x,y=y,z=z,images=images)

@bp.route('/')
def index():
    return redirect(url_for('locations.show',val='0_0_0_6'))

add_blueprint(bp)
# - images = @location.images.map { |img| { 'name' => img.label, 'id' => img.id, 'download' => "/images/#{img.id}/download", 'url' => "/images/#{img.id}/download",
#   'intent' => (img.stat.capitalize + ':') }.update(img.options) }
# - options = { panzoomEnabled: false, xyz: [@location.x, @location.y, @location.z]}
# = render :partial => 'shared/viewer', :locals => { :images => images, :options => options }
