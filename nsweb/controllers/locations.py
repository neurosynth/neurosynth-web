from nsweb.core import cache
from nsweb.api.utils import make_cache_key
from nsweb.api.locations import get_params
from flask import Blueprint, render_template


bp = Blueprint('locations', __name__, url_prefix='/locations')


@bp.route('/')
@bp.route('/<string:val>/')
@cache.cached(timeout=3600, key_prefix=make_cache_key)
def show(val=None):
    x, y, z, radius = get_params(val)
    return render_template('locations/index.html', radius=radius,
                           x=x, y=y, z=z)
