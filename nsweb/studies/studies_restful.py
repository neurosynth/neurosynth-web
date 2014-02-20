from flask_restful import Resource
from nsweb.core import app
from nsweb.core import api
from nsweb.models import studies

class Study(Resource):
    def get(self):
        return studies.Study.query.all() #use paginate() plz

api.add_resource(Study,'/')

if __name__ == '__main__':
    app.run(debug=True)