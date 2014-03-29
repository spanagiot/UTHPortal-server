#!/usr/bin/env python
# -*- coding: utf-8 -*-

# periodic asynchronous scrapping coordinator

# TODO:
# Get proper link for courses
# Logging and testing

# import gevent.monkey and apply the patch for async operations
import gevent.monkey
gevent.monkey.patch_all()
from gevent.queue import Queue
from gevent.pool import Pool

import sys
import logging
import logging.config
from time import sleep
from Queue import PriorityQueue

from library.util import fetch_html, get_bsoup
from library.inf import update_course, update_announcements
from library.food import fetch_food_menu

from pymongo import MongoClient
from datetime import datetime

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

SLEEP_INTERVAL = 2

client = None
db = None

"""
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
"""


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

    logger.debug('Initializing succeed!')


    fetch_food_menu()
    update_announcements()

    courses_codes = [ course['code'] for course in db.inf.courses.find() ]

    # Queue the jobs
    for code in courses_codes:
        db.queue.insert( {'code':code} )

    while True:
        # Get all the jobs from the queue
        jobs = db.queue.find()
        logger.debug('Got %d jobs!' % jobs.count())

        if jobs.count() == 0:
            sleep(SLEEP_INTERVAL)
            continue

        # Pop the next jobs (TODO: group jobs)
        next_jobs = list()
        for job in jobs:
            next_jobs.append(job['code'])
            db.queue.remove(job)

        # Fetch the course
        fetch_courses(next_jobs)

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


def fetch_course(code, *args, **kargs):
    fetch_courses( [ code ], *args, **kargs)


def fetch_courses(codes, n_workers=1, timeout_secs=10, n_tries=3):
    """
    """

    # Initialize a pool of 'n_workers' greenlets
    n_workers = len(codes)
    worker_pool = Pool(n_workers)

    # Enqueue the tasks
    for code in codes:
        #update_course(code, timeout_secs, n_tries)
        worker_pool.spawn( update_course, code, timeout_secs, n_tries )

    worker_pool.join()


if __name__ == '__main__':
    main()

# Spawn workers till there are no more tasks
#while ( not task_queue.empty() ):
#    gevent.sleep(0.1)
#
#    # Find the best number of workers to spawn
#    n_spawns = min( task_queue.qsize(), worker_pool.free_count() )
#
#    # Spawn 'n_spawns' workers
#    for i in xrange(0, n_spawns):
#        worker_pool.spawn( update_course(, timeout_secs, n_tries)

# Wait for all the workers to finish
"""

#def fetch_course(course_name, timeout_secs=10, n_tries=3):
#    fetch_courses(course_name,




# define a testbench function and run it if the module is run directly
if __name__ == '__main__':
    def testbench():
        data = fetch_courses(1, 10, 3)

        #print(data['ce120'][-13][0].date())
        ##print(data['ce120'][-13][1])
        #print(data['ce232'][-5][0].date())
        #print(data['ce232'][-5][1])

    testbench()
"""
