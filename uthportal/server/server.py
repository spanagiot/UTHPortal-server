#!/usr/bin/env python
# -*- coding: utf-8 -*-

# (HTTP REST API) JSON serving Flask app

import flask
from pymongo import MongoClient
from json import JSONEncoder

from bs4 import BeautifulSoup
from datetime import datetime, timedelta

app = flask.Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['JSON_SORT_KEYS'] = True
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
#app.debug = True

HTTPCODE_NOT_FOUND = 404
HTTPCODE_NOT_IMPLEMENTED = 501

client = MongoClient()
db = client.uthportal

# Overide class for JSONEncoder
class BSONEncoderEx(JSONEncoder):
    def default(self, obj, **kwargs):
        from bson.objectid import ObjectId
        from datetime import datetime

        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        else:
            return JSONEncoder.default(self, obj, **kwargs)

# Set the default flask app encoder to the above encoder
app.json_encoder = BSONEncoderEx

@app.route('/inf/courses/all')
def show_courses():
    db_courses = db.inf.courses.find()

    # Remove not needed keys #
    courses = [ ]
    for doc in db_courses:
        del doc['announcements']
        del doc['_id']
        courses.append(doc)

    courses = { doc['code']:doc for doc in courses }
    return flask.jsonify(courses)


@app.route('/inf/courses/<course_name>')
def show_course(course_name):
    db_doc = db.inf.courses.find_one({'code':course_name })

    if isinstance(db_doc, dict):
        return flask.jsonify(db_doc)
    else:
        flask.abort(HTTPCODE_NOT_FOUND)

@app.route('/inf/announce/<type>')
def show_inf_announcements(type):
    db_doc = db.inf.announce.find_one({'type': type})

    if isinstance(db_doc, dict):
        return flask.jsonify(db_doc)
    else:
        flask.abort(HTTPCODE_NOT_IMPLEMENTED)

@app.route('/uth/rss/<type>')
def show_uth_announcements(type):
    db_doc = db.uth.rss.find_one({'type': type})

    if isinstance(db_doc, dict):
        return flask.jsonify(db_doc)
    else:
        flask.abort(HTTPCODE_NOT_IMPLEMENTED)

@app.route('/uth/food-menu')
def show_food_menu():
    _monday = (datetime.now() - timedelta(datetime.now().weekday())).date()
    last_monday = datetime.combine(_monday, datetime.min.time() )

    db_doc = db.uth.food_menu.find_one({'date':last_monday })
    if isinstance(db_doc, dict):
        return flask.jsonify(db_doc)
    else:
        flask.abort(HTTPCODE_NOT_IMPLEMENTED)


# http://forums.udacity.com/questions/6009973/how-to-use-the-jinja2-template-engine-with-appengine
import os
import jinja2

jinja_environment = jinja2.Environment(autoescape=True,
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))

@app.route('/')
def index():
    courses = {}

    for course in db.inf.courses.find():
        courses[ course['code'] ] = course['info']['name']

    template = jinja_environment.get_template('index.html')
    return template.render( courses=courses )

def json_error(code, message):
    return flask.jsonify( {'error': {'code': code, 'message': message} } ), code

@app.errorhandler(HTTPCODE_NOT_FOUND)
def page_not_found(error):
    return json_error(HTTPCODE_NOT_FOUND,'Page not Found')

@app.errorhandler(HTTPCODE_NOT_IMPLEMENTED)
def not_implemented(error):
    return json_error(HTTPCODE_NOT_IMPLEMENTED,'Not implemented')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
