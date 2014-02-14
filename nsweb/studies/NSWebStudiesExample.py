# REMOVE THIS FILE. switched from flask-restful to flask-restless b/c it didn't get along with flask-sqlalchemy, but it could have been config error

app = Flask(__name__)
api = restful.Api(app)

class Studies(restful.Resource):
    def get(self):
        return articles

api.add_resource(Studies, '/')

if __name__ == '__main__':
    app.run(debug=True)