from nsweb.controllers.api import bp
from flask import request, jsonify, url_for
from nsweb.models.analyses import TermAnalysis, AnalysisSet, TopicAnalysis

@bp.route('/terms/')
def list_terms():

    results_per_page = int(request.args['length'])
    offset = int(request.args['start'])

    order_by = '{0} {1}'.format(
        ['name', 'n_studies', 'n_activations'][int(request.args['order[0][column]'])],
        str(request.args['order[0][dir]']))
    search = str(request.args['search[value]']).strip()

    data = TermAnalysis.query
    if search:  # No empty search on my watch
        search = '%{}%'.format(search)
        data = data.filter(TermAnalysis.name.like(search) |
                           TermAnalysis.n_studies.like(search) |
                           TermAnalysis.n_activations.like(search))
    data = data.order_by(order_by)
    data = data.paginate(page=(offset/results_per_page)+1,
                         per_page=results_per_page, error_out=False)
    result = {}
    result['draw'] = int(request.args['draw'])  # for security
    result['recordsTotal'] = TermAnalysis.query.count()
    result['recordsFiltered'] = data.total
    result['data'] = [
        ['<a href={0}>{1}</a>'.format(
            url_for('analyses.show_term', term=d.name), d.name),
                            d.n_studies,
                            d.n_activations,
                            ] for d in data.items]
    result = jsonify(**result)
    return result

@bp.route('/topics/')
def list_topic_sets():
    topic_sets = AnalysisSet.query.all()
    data = [[
        '<a href={0}>{1}</a>'.format(
            url_for('analyses.show_topic_set', topic_set=ts.name),
                    ts.name),
        ts.description,
        ts.n_analyses] for ts in topic_sets]
    return jsonify(data=data)

@bp.route('/topics/<string:val>/')
def list_topics(val):
    ts = AnalysisSet.query.filter_by(name=val).first()
    data = [
        ['<a href={0}>{1}</a>'.format(
            url_for('analyses.show_topic', topic_set=ts.name,
                    number=t.number), 'Topic %d' % t.number),
         t.terms,
         t.n_studies
        ] for t in ts.analyses]
    return jsonify(data=data)

@bp.route('/analyses/<string:name>/')
def find_api_analysis(name):
    """ If the passed val isn't numeric, assume it's a analysis name,
    and retrieve the corresponding numeric ID. 
    """
    val = Analysis.query.filter_by(name=name).first().id
    return redirect(url_for('analyses.api', id=val))

@bp.route('/analyses/<int:val>/')
def analyses_api(val):
    data = Analysis.query.get(val)
#     data=Frequency.query.filter_by(analysis_id=int(val))#attempted optimization. Join causes slower performance however
    data = [['<a href={0}>{1}</a>'.format(url_for('studies.show', val=f.pmid) , f.study.title),
              f.study.authors,
              f.study.journal,
              round(f.frequency, 3),
              ] for f in data.frequencies]
    data = jsonify(aaData=data)
    return data