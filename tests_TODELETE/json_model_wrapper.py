from flask.json import jsonify

def restless_json(page_num,objects,total_pages):
    num_results=len(objects)
    return jsonify(dict(page=page_num, objects=objects, total_pages=total_pages, num_results=num_results))