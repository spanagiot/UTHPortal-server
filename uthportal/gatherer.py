#!/usr/bin/env python
# -*- coding: utf-8 -*-

# periodic asynchronous scrapping coordinator

# TODO:
# Get proper link for courses
# Logging and testing

import gevent.monkey
gevent.monkey.patch_all()
from gevent.queue import Queue
from gevent.pool import Pool

import sys
import logging
import logging.config
from time import sleep

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

inactive_loggers = { 'requests', 'apscheduler', 'urllib3' }
for log in inactive_loggers:
    _logger = logging.getLogger(log)
    _logger.setLevel(logging.ERROR)

logger = logging.getLogger(__name__)

################################################################

from library.food import fetch_food_menu
from library.inf import fetch_general_announcements, update_course
from library.util import fetch_html, get_bsoup

from pymongo import MongoClient
from datetime import datetime

from apscheduler.scheduler import Scheduler

##############################################################
MONGO_DB_URI = 'mongodb://localhost:27017/'

client = None
db = None

sched = Scheduler(standalone=True)
##############################################################

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


def main():
    if not health_check():
        logger.error('Health check FAILED! Terminating...')
        sys.exit(1)

    init_db()

    logger.debug('Initializing succeed!')

    sched.add_interval_job( fetch_food_menu, minutes=60 )
    sched.add_interval_job( fetch_general_announcements, minutes=10 )

    try:
        sched.start()
    except (KeyboardInterrupt):
        logger.debug('Terminating...')

@sched.interval_schedule(minutes=10)
def fetch_courses(n_workers=1, timeout_secs=10, n_tries=3):
    """
    """
    logger.debug('Now will fetch courses');
    codes = [ course['code'] for course in db.inf.courses.find() ]

    # Initialize a pool of 'n_workers' greenlets
    n_workers = len(codes)
    worker_pool = Pool(n_workers)

    # Enqueue the tasks
    for code in codes:
        #update_course(code, timeout_secs, n_tries)
        worker_pool.spawn( update_course, code, timeout_secs, n_tries )

    worker_pool.join()

def fetch_course(code, *args, **kargs):
    fetch_courses( [ code ], *args, **kargs)


if __name__ == '__main__':
    main()

