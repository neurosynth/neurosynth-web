from flask import Blueprint, render_template, redirect, url_for, abort
from nsweb.models.analyses import CustomAnalysis
from nsweb.api.custom import run_custom_analysis as api_run_custom
import json
from flask_user import login_required, current_user
from nsweb.initializers import settings
from nsweb.controllers import error_page
from os.path import join


bp = Blueprint('custom_analyses', __name__, url_prefix='/analyses')


@bp.route('/custom/<string:uid>/')
def show_custom_analysis(uid):
    custom = CustomAnalysis.query.filter_by(uuid=uid).first()
    if custom is None or (custom.private and custom.user != current_user):
        return render_template('analyses/missing.html', analysis=uid)
    return render_template('analyses/custom/show.html', analysis=custom)


@bp.route('/custom/')
def list_custom_analyses():
    return render_template('analyses/custom/index.html')


@bp.route('/browse/')
def browse_public_analyses():
    executed_analyses = CustomAnalysis.query.filter(
        CustomAnalysis.last_run_at != None)
    analyses = executed_analyses.filter(CustomAnalysis.private == False).all()
    analyses += executed_analyses.filter(CustomAnalysis.private == None).all()
    return render_template('analyses/custom/browse_public.html',
                           analyses=analyses)


@bp.route('/custom/faq/')
def faq_custom_analyses():
    data = json.load(open(join(settings.ROOT_DIR, 'data', 'json',
                               'faq_custom_analyses.json')))
    return render_template('home/faq_custom_analyses.html', data=data)


@bp.route('/custom/run/<string:uid>/', methods=['GET', 'POST'])
@login_required
def run_custom_analysis(uid):
    """
    Given a uuid, kick off the analysis run and redirect the user to the
    results page once the analysis is complete.
    """
    custom = CustomAnalysis.query.filter_by(uuid=uid).first()

    if not custom or not custom.studies:
        abort(404)

    result = api_run_custom(uid)

    if result is None:
        return error_page("An unspecified error occurred while trying "
                          "to run the custom meta-analysis. Please try "
                          "again.")

    return redirect(url_for('analyses.show_custom_analysis', uid=uid))
