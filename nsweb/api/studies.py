from nsweb.api import bp
from flask import jsonify
from nsweb.api.schemas import StudySchema
from nsweb.models.studies import Study
from nsweb.core import cache


@bp.route('/studies/<int:pmid>/')
@cache.memoize(timeout=3600)
def get_study(pmid):
    """
    Get data for a single study
    ---
    tags:
        - studies
    responses:
        200:
            description: A study
        default:
            description: Study not found
    parameters:
        - in: path
          name: pmid
          description: PubMed ID of the study
          type: integer
          required: true
    """
    study = Study.query.get(pmid)
    schema = StudySchema()
    return jsonify(data=schema.dump(study).data)
