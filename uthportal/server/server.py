#!/usr/bin/env python
# -*- coding: utf-8 -*-

# (HTTP REST API) JSON serving Flask app

import flask
from pymongo import MongoClient
from json import JSONEncoder

app = flask.Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['JSON_SORT_KEYS'] = True
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

HTTPCODE_NOT_FOUND = 404
HTTPCODE_NOT_IMPLEMENTED = 501

client = MongoClient()

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

app.json_encoder = BSONEncoderEx

@app.route('/inf/courses/all')
def show_courses():
    db_courses = client.uthportal.inf.courses.find()
    courses = { doc['code']:doc for doc in db_courses }
    return flask.jsonify(courses)


@app.route('/inf/courses/<course_name>')
def show_course(course_name):
    db_doc = client.uthportal.inf.courses.find_one({'code':course_name })
    if isinstance(db_doc, dict):
        return flask.jsonify(db_doc)
    else:
        flask.abort(HTTPCODE_NOT_FOUND)

@app.route('/uth/food-menu')
def show_food_menu():
    db_doc = client.uthportal.uth.food_menu.find_one({'name':'food_menu'})
    if isinstance(db_doc, dict):
        return flask.jsonify(db_doc)
    else:
        flask.abort(HTTPCODE_NOT_IMPLEMENTED)

def json_error(code, message):
    return flask.jsonify( {'error': {'code': code, 'message': message} } ), code

@app.errorhandler(HTTPCODE_NOT_FOUND)
def page_not_found(error):
    return json_error(HTTPCODE_NOT_FOUND,'Page not Found')

@app.errorhandler(HTTPCODE_NOT_IMPLEMENTED)
def not_implemented(error):
    return json_error(HTTPCODE_NOT_IMPLEMENTED,'Not implemented')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
