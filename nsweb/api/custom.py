from flask import Blueprint, request, jsonify, abort
from nsweb.models.analyses import CustomAnalysis
from nsweb.models.studies import Study
from nsweb.models.frequencies import Frequency
from nsweb.core import db
from flask_login import current_user
from flask_user import login_required
import datetime as dt
import json
import uuid


bp = Blueprint('api_analyses', __name__, url_prefix='/api/analyses/custom')


@bp.route('/save/', methods=['POST', 'GET'])
@login_required
def save_custom_analysis():
    """
    Expects a JSON string with the following schema:
      'data':
        'uuid': (optional) uuid of existing analysis to update
        'name': (optional) name of analysis
        'studies': List of PMIDs
    :return:
    """
    data = json.loads(request.form['data'])
    name = data.get('name')
    uid = data.get('uuid')
    studies = data.get('studies', [])
    description = data.get('description')
    private = data.get('private')
    pmids = [int(x) for x in studies]

    # Verify that all requested pmids are in the database
    for pmid in pmids:
        study = Study.query.filter_by(pmid=pmid).first()
        if not study:
            return jsonify(
                dict(result='error', error='Invalid PMID: %s' % pmid))

    if uid:
        custom_analysis = CustomAnalysis.query.filter_by(
            uuid=uid, user_id=current_user.id).first()
        if not custom_analysis:
            return jsonify(
                dict(result='error', error='No matching analysis found.'))
        if name:
            custom_analysis.name = name
        if description is not None:
            custom_analysis.description = description
        custom_analysis.private = private
    else:
        # create new custom analysis
        uid = str(uuid.uuid4())[:18]
        custom_analysis = CustomAnalysis(
            uuid=uid, name=name, description=description,
            user_id=current_user.id, private=private)
    # Explicitly update timestamp, because it won't be changed if only studies
    # are modified, and we need to compare this with last_run_at later.
    custom_analysis.updated_at = dt.datetime.utcnow()
    custom_analysis.n_studies = len(pmids)
    db.session.add(custom_analysis)
    db.session.commit()

    Frequency.query.filter_by(analysis_id=custom_analysis.id).delete()
    for pmid in pmids:
        freq = Frequency.query.filter_by(
            analysis_id=custom_analysis.id, pmid=pmid).first()
        if not freq:
            freq = Frequency(analysis_id=custom_analysis.id, pmid=pmid)
            db.session.add(freq)
    db.session.commit()

    return jsonify(dict(result='success', uuid=uid, id=custom_analysis.id))


@bp.route('/<string:uid>/', methods=['GET'])
def get_custom_analysis(uid):
    """
    Given a uuid return JSON blob representing the custom analysis information
    and a list of its associated studies

    We're assuming that the user doesn't have to be logged in and that anyone
    can access the analysis if they know its uuid. This makes it easy for users
    to share links to their custom analyses.
    """
    custom = CustomAnalysis.query.filter_by(uuid=uid).first()
    if not custom:
        abort(404)
    if current_user.id != custom.user_id and (custom.private or not
                                              custom.last_run_at):
        abort(403)
    return jsonify(custom.serialize())


@bp.route('/all/', methods=['GET'])
@login_required
def get_custom_analyses():
    """
    :return: All stored custom analyses for the requesting user
    """
    response = {
        'analyses': [custom.serialize() for custom in
                     CustomAnalysis.query.filter_by(user_id=current_user.id)]
    }
    return jsonify(response)


@bp.route('/copy/<string:uid>/', methods=['POST'])
@login_required
def copy_custom_analysis(uid):
    """
    Given a uuid of an existing analysis, create a clone of the analysis with
    a new uuid
    :param uuid:
    :return: JSON blob including the new uuid
    """
    custom = CustomAnalysis.query.filter_by(uuid=uid).first()
    if not custom:
        abort(404)

    uid = str(uuid.uuid4())[:18]
    new_custom = CustomAnalysis(
        uuid=uid, user_id=current_user.id, name=custom.name)
    db.session.add(new_custom)
    db.session.commit()

    for freq in custom.frequencies.all():
        new_freq = Frequency(analysis_id=new_custom.id, pmid=freq.pmid)
        db.session.add(new_freq)
    db.session.commit()

    response = dict(uuid=uid, result="success")
    return jsonify(response)


@bp.route('/<string:uid>/', methods=['DELETE'])
@login_required
def delete_custom_analysis(uid):
    """
    Given a uuid of an existing analysis, delete it.

    :param uuid:
    :return:
    """
    custom = CustomAnalysis.query.filter_by(uuid=uid).first()
    if not custom:
        abort(404)
    if custom.user_id != current_user.id:
        abort(403)
    # TODO: instead of deleting, consider setting a deleted flag instead
    db.session.delete(custom)
    db.session.commit()
    return jsonify(dict(result='success'))
