from flask import Blueprint, render_template, redirect, url_for, abort
from nsweb.models.analyses import (Analysis, AnalysisSet, TopicAnalysis,
                                   TermAnalysis)
import json
import re
from flask_user import login_required, current_user
from nsweb.initializers import settings
from nsweb.controllers import error_page
from os.path import join


bp = Blueprint('analyses', __name__, url_prefix='/analyses')


### TOP INDEX ###
@bp.route('/')
def list_analyses():
    n_terms = TermAnalysis.query.count()
    return render_template('analyses/index.html', n_terms=n_terms)


### ROUTES COMMON TO ALL ANALYSES ###
def find_analysis(name, type=None):
    ''' Retrieve analysis by either id (when int) or name (when string) '''
    if re.match('\d+$', name):
        return Analysis.query.get(name)
    query = Analysis.query.filter_by(name=name)
    if type is not None:
        query = query.filter_by(type=type)
    return query.first()


@bp.route('/<string:id>/')
def show_analysis(id):
    analysis = find_analysis(id)
    if analysis is None:
        return render_template('analyses/missing.html', analysis=id)
    if analysis.type == 'term':
        return redirect(url_for('analyses.show_term', term=analysis.name))
    elif analysis.type == 'topic':
        return redirect(url_for('analyses.show_topic', number=analysis.number,
                                topic_set=analysis.analysis_set.name))


@bp.route('/terms/')
def list_terms():
    return render_template('analyses/terms/index.html')


@bp.route('/terms/<string:term>/')
def show_term(term):
    analysis = find_analysis(term, type='term')
    if analysis is None:
        return render_template('analyses/missing.html', analysis=term)
    return render_template('analyses/terms/show.html',
                           analysis=analysis,
                           cog_atlas=json.loads(analysis.cog_atlas or '{}'))


### TOPIC-SPECIFIC ROUTES ###
@bp.route('/topics/')
def list_topic_sets():
    topic_sets = AnalysisSet.query.filter_by(type='topics')
    return render_template('analyses/topics/index.html',
                           topic_sets=topic_sets)


@bp.route('/topics/<string:topic_set>/')
def show_topic_set(topic_set):
    topic_set = AnalysisSet.query.filter_by(name=topic_set).first()
    return render_template('analyses/topics/show_set.html',
                           topic_set=topic_set)


@bp.route('/topics/<string:topic_set>/<string:number>')
def show_topic(topic_set, number):
    topic = TopicAnalysis.query.join(AnalysisSet).filter(
        TopicAnalysis.number == number, AnalysisSet.name == topic_set).first()
    if topic is None:
        return render_template('analyses/missing.html', analysis=None)
    terms = [t[0] for t in TermAnalysis.query.with_entities(
        TermAnalysis.name).all()]
    top = topic.terms.split(', ')

    def map_url(x):
        if x in terms:
            return '<a href="%s">%s</a>' % (url_for('analyses.show_term',
                                                    term=x), x)
        return x
    topic.terms = ', '.join(map(map_url, top))
    return render_template('analyses/topics/show.html',
                           analysis_set=topic.analysis_set, analysis=topic)


# Show custom analysis page for explanation
@bp.route('/custom/')
def list_custom_analyses():
    return render_template('analyses/custom/index.html')
