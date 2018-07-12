""" DataTables API routes. These are just wrappers around the routes in
the operations module. """

from nsweb.api import bp
from flask import jsonify, request, url_for
from nsweb.models.genes import Gene


@bp.route('/dt/genes/')
def datatable_genes():

    results_per_page = int(request.args['length'])
    offset = int(request.args['start'])

    order_by = '{0} {1}'.format(
        ['symbol', 'name', 'synonyms', 'locus_type']
        [int(request.args['order[0][column]'])],
        str(request.args['order[0][dir]']))
    search = str(request.args['search[value]']).strip()

    data = Gene.query
    if search:
        search = '%{}%'.format(search)
        data = data.filter(Gene.name.like(search) |
                           Gene.symbol.like(search) |
                           Gene.synonyms.like(search))
    data = data.order_by(order_by)
    data = data.paginate(page=(offset / results_per_page) + 1,
                         per_page=results_per_page, error_out=False)
    result = {}
    result['draw'] = int(request.args['draw'])  # for security
    result['recordsTotal'] = Gene.query.count()
    result['recordsFiltered'] = data.total
    result['data'] = [
        ['<a href={0}>{1}</a>'.format(
            url_for('genes.show', symbol=d.symbol), d.symbol),
         d.name,
         d.synonyms,
         d.locus_type
         ] for d in data.items]
    return jsonify(**result)
