#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import sys
from Queue import PriorityQueue
from pymongo import MongoClient
from gatherer.gatherer import fetch_courses

# Initialize logging
LOGGING_FILE_PATH = 'logging.conf'

try:
    import json

    with open(LOGGING_FILE_PATH, 'r') as f:
        log_json = f.read()

    log_dict = json.loads(log_json)
    logging.config.fileConfig(log_dict)
except IOError:
    print 'ERROR: Cannot read %s' % LOGGING_FILE_PATH
    sys.exit(1)
except ValueError:
    print 'ERROR: File is not a valid JSON object'
    sys.exit(1)


logger = logging.getLogger(__name__)



MONGO_DB_URI = 'mongodb://localhost:27017/'

PRIORITY_LOW = 3
PRIORITY_MEDIUM = 2
PRIORITY_HIGH = 1

tasks = PriorityQueue()
client = None
db = None

class QueueItem():
    def __init__(self, function, priority, *args, **kargs):
        self.priority = priority
        self.function = function
        self.args = args
        self.kargs = kargs

    def __cmp__(self, other):
        return cmp(self.priority, other.priority)

    def run(self):
        return self.function(self.args, self.kargs)


def health_check():
    try:
        client = MongoClient(MONGO_DB_URI)
        db = client.uthportal
    except:
        return False

def main():
    if not health_check():
        return

    init_db()

    courses_codes = [ course.code for course in db.inf.courses.find() ]
    for code in courses_codes:
        tasks.put(QueueItem(PRIORITY_MEDIUM))

def init_db():
    from data import courses_data

    # TODO: Check if db exists(else create), collections, documtents etc

    for course in courses_data:
        db.inf.courses.insert(courses_data[course])

if __name__ == '__main__':
    main()
