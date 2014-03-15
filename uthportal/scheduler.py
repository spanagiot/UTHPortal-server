#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gatherer import fetch_course, fetch_courses
'''
gatherer imports gevent monkey and patches 'thread'
this means that we have to FIRST import fetch_courses
and then anything else that may import threading,
otherwise Exception KeyError: KeyError is thrown.
if threading module is loaded before monkey-patching,
_get_ident() call returns one value when _MainThread instance is
created and added to _active, and another value at the time
_exitfunc() is called - hence KeyError in del _active[_get_ident()].
'''
import sys
import logging
import logging.config
from Queue import PriorityQueue

from pymongo import MongoClient
from datetime import datetime

import gatherer

# Initialize logging ##############################################
LOGGING_FILE_PATH = 'logging.conf'

try:
    import json

    with open(LOGGING_FILE_PATH, 'r') as f:
        log_json = f.read()

    log_dict = json.loads(log_json)
except IOError:
    print 'ERROR: Cannot read %s' % LOGGING_FILE_PATH
except ValueError:
    print 'ERROR: logging.conf is not a valid JSON object'
except Exception as ex:
    print 'ERROR: %s' % ex
finally:
    if log_dict is None:
        sys.exit(1)

try:
    logging.config.dictConfig(log_dict)
except Exception as ex:
    print ex
    sys.exit(1)

logger = logging.getLogger(__name__)

################################################################

MONGO_DB_URI = 'mongodb://localhost:27017/'

PRIORITY_LOW = 3
PRIORITY_MEDIUM = 2
PRIORITY_HIGH = 1

tasks = PriorityQueue()
client = None
db = None

class QueueItem():
    def __init__(self, function, datetime, priority, *args, **kargs):
        self.priority = priority
        self.function = function
        self.datetime = datetime
        self.args = args
        self.kargs = kargs

    def __cmp__(self, other):
        if self.datetime != other.datetime:
            return cmp(self.datetime, other.datetime)
        return cmp(self.priority, other.priority)

    def run(self):
        return self.function(self.args, self.kargs)


def health_check():
    from pymongo.errors import ConnectionFailure
    global db, client

    try:
        client = MongoClient(MONGO_DB_URI)
        db = client.uthportal
    except ConnectionFailure:
        logger.error('MongoDB connection failure at: %s' % MONGO_DB_URI)
        return False

    return True

def main():
    if not health_check():
        logger.error('Health check FAILED! Terminating...')
        sys.exit(1)

    init_db()




    courses_codes = [ course['code'] for course in db.inf.courses.find() ]
    for code in courses_codes:
        item = QueueItem()

        function = fetch_course(
        priority = PRIORITY_HIGH

        tasks.put(item)

def init_db():
    from data import courses_data

    # TODO: Check if db exists(else create), collections, documtents etc

    for course in courses_data:
        find_query = { 'code' : course }

        if db['inf.courses'].find(find_query).count() > 0:
            # TODO UPDATE
            pass
        else:
            db['inf.courses'].insert(courses_data[course])

if __name__ == '__main__':
    main()
