import flask
from pymongo import MongoClient
from json import JSONEncoder

app = flask.Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['JSON_SORT_KEYS'] = True
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

client = MongoClient()

# Overide class for JSONEncoder
class BSONEncodeEx(JSONEncoder):
    def default(self, obj, **kwargs):
        from bson.objectid import ObjectId
        from datetime import datetime
        
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        else:            
            return JSONEncoder.default(self, obj, **kwargs)

app.json_encoder = BSONEncodeEx

@app.route('/inf/courses/all')
def fetch_courses():
    db_courses = client.uthportal.inf.courses.find()
    courses = { doc['code']:doc for doc in db_courses }
    return flask.jsonify(courses)


@app.route('/inf/courses/<course_name>')
def fetch_course(course_name):
    db_doc = client.uthportal.inf.courses.find_one({'code':course_name })
    if isinstance(db_doc, dict):
        return flask.jsonify(db_doc)
    else:
        flask.abort(404)

@app.errorhandler(404)
def page_not_found(error):
    return flask.jsonify( { 'error': { 'code' : 404, 'message': 'Page not found' } } )
    

if __name__ == '__main__':
    app.run(debug=True)
