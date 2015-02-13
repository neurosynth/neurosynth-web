from flask import Blueprint, render_template, redirect, url_for, request, jsonify, abort, session, g
from flask.ext.login import current_user
from flask.ext.user import login_required
from nsweb.models.analyses import Analysis, AnalysisSet, TopicAnalysis, TermAnalysis, CustomAnalysis
from nsweb.core import add_blueprint
from flask.helpers import url_for
import json
import re
import uuid

bp = Blueprint('analyses', __name__, url_prefix='/analyses')
 
### ROUTES COMMON TO ALL ANALYSES ###
def find_analysis(val):
    ''' Retrieve analysis by either id (when int) or name (when string) '''
    return Analysis.query.get(val) if re.match('\d+$', val) else \
        Analysis.query.filter_by(name=val).first()

@bp.route('/<string:val>/images')
def get_images(val):
    analysis = find_analysis(val)
    images = [{
        'id': img.id,
        'name': img.label,
        'colorPalette': 'red' if 'reverse' in img.label else 'blue',
        # "intent": (img.stat + ':').capitalize(),
        'url': '/images/%s' % img.id,
        'visible': 1 if 'reverse' in img.label else 0,
        'download': '/images/%s' % img.id,
        'intent': 'z-score'
    } for img in analysis.images if img.display]
    return jsonify(data=images)

@bp.route('/<string:val>/images/reverseinference/')
def get_reverse_inference_image(val):
    # Horrible hacks here to serve just reverse inference images with or
    # without FDR; totally mucks up API pattern, so clean up later.
    analysis = find_analysis(val)
    fdr = ('nofdr' not in request.args.keys())
    img = [i for i in analysis.images if 'reverse' in i.label][0]
    from nsweb.controllers import images
    return images.download(img.id, fdr)

@bp.route('/<string:val>/studies')
def get_studies(val):
    analysis = find_analysis(val)
    if 'dt' in request.args:
        data = []
        for f in analysis.frequencies:
            s = f.study
            link = '<a href={0}>{1}</a>'.format(url_for('studies.show',val=s.pmid),s.title)
            data.append([link, s.authors, s.journal, round(f.frequency, 3)])
        data = jsonify(data=data)
    else:
        data = jsonify(studies=[s.pmid for s in analysis.studies])
    return data


### TOP INDEX ###
@bp.route('/')
def list_analyses():
    n_terms = TermAnalysis.query.count()
    return render_template('analyses/index.html.slim', n_terms=n_terms)

### TERM-SPECIFIC ROUTES ###
@bp.route('/term_names/')
def get_term_names():
    names = [f.name for f in TermAnalysis.query.all()]  # optimize this later--select only names
    return jsonify(data=names)

@bp.route('/terms/')
def list_terms():
    return render_template('analyses/terms/index.html.slim')
    
@bp.route('/terms/<string:term>/')
def show_term(term):
    analysis = find_analysis(term)
    if analysis is None:
        return render_template('analyses/missing.html.slim', analysis=term)
    return render_template('analyses/terms/show.html.slim',
                           analysis=analysis,
                           cog_atlas=json.loads(analysis.cog_atlas or '{}'))

### TOPIC-SPECIFIC ROUTES ###
@bp.route('/topics/')
def list_topic_sets():
    topic_sets = AnalysisSet.query.filter_by(type='topics')
    return render_template('analyses/topics/index.html.slim',
                           topic_sets=topic_sets)

@bp.route('/topics/<string:topic_set>/')
def show_topic_set(topic_set):
    topic_set = AnalysisSet.query.filter_by(name=topic_set).first()
    return render_template('analyses/topics/show_set.html.slim',
                           topic_set=topic_set)

@bp.route('/topics/<string:topic_set>/<string:number>')
def show_topic(topic_set, number):
    topic = TopicAnalysis.query.join(AnalysisSet).filter(
        TopicAnalysis.number == number, AnalysisSet.name == topic_set).first()
    if topic is None:
        return render_template('analyses/missing.html.slim', analysis=None)
    terms = [t[0] for t in TermAnalysis.query.with_entities(TermAnalysis.name).all()]
    top =topic.terms.split(', ')
    def map_url(x):
        if x in terms:
            return '<a href="%s">%s</a>' % (url_for('analyses.show_term', term=x), x)
        return x
    topic.terms = ', '.join(map(map_url, top))
    return render_template('analyses/topics/show.html.slim',
                           analysis_set=topic.analysis_set, analysis=topic)

### FALLBACK GENERIC ROUTE ###
@bp.route('/<string:id>/')
def show_analysis(id):
    analysis = find_analysis(id)
    if analysis is None:
        return render_template('analyses/missing.html.slim', analysis=id)
    if analysis.type == 'term':
        return redirect(url_for('analyses.show_term', term=analysis.name))
    elif analysis.type == 'topic':
        return redirect(url_for('analyses.show_topic', number=analysis.number,
                                topic_set=analysis.analysis_set.name))


@bp.route('/custom/save/', methods=['POST', 'GET'])
@login_required
def save_custom_analysis():
    """
    Expects a JSON object called 'data' with the following schema:
        'uuid': (optional) uuid of existing to save the object to
        'studies': List of PMIDs
    :return:
    """
    data = json.loads(request.form['data'])
    if 'uuid' in data:
        pass
    else:
        # create new custom analysis
        u = unicode(uuid.uuid4())[:18]
        custom_analysis = CustomAnalysis(uuid=u)
        pass

    for pmid in data['studies']:
        # create new study/analysis item
        print pmid

    return jsonify(dict(username=current_user.username))

@bp.route('/custom/get/<string:uuid>/', methods=['GET'])
def get_custom_analysis(uuid):
    """
    Given a uuid return JSON blob representing the custom analysis information
    and a list of its associated studies

    We're assuming that the user doesn't have to be logged in and that anyone
    can access the analysis if they know its uuid. This makes it easy for users to
    share links to their cusotm analyses.
    """
    return jsonify(dict(result='not implemented'))


@bp.route('/custom/run/<string:uuid>/', methods=['POST'])
def run_custom_analysis(uuid):
    """
    Given a uuid, kick off the analysis run and redirect the user to the results page once
    the analysis is complete.
    """
    return jsonify(dict(result='not implemented'))


@bp.route('/custom/copy/<string:uuid>/', methods=['POST'])
def copy_custom_analysis(uuid):
    """
    Given a uuid of an existing analysis, create a clone of the analysis with a new uuid
    :param uuid:
    :return: JSON blob including the new uuid
    """
    return jsonify(dict(result='not implemented'))


@bp.route('/custom/<string:uuid>/', methods=['DELETE'])
def delete_custom_analysis(uuid):
    """
    Given a uuid of an existing analysis, delete it.

    :param uuid:
    :return:
    """
    return jsonify(dict(result='not implemented'))


add_blueprint(bp)
