from flask_restful import Resource
from nsweb.core import app
from nsweb.core import api
from nsweb.models import features

class Study(Resource):
    def get(self):
        return features.Feature.query.all()

api.add_resource(Study,'/')

if __name__ == '__main__':
    app.run(debug=True)