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
from library.uth import update_rss
from library.util import fetch_html, get_bsoup

from pymongo import MongoClient
from datetime import datetime, timedelta

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
    from data import instructions

    # TODO: Check if db exists(else create), collections, documents, etc
    for (db_path, (db_entry, query)) in instructions.items():
        for (key, document) in db_entry.items():
            # Unique query to find the document
            find_query = { query : key }

            # Number of entries of that query
            n_entries = db[db_path].find(find_query).count()

            if n_entries == 0:
                db[db_path].insert(document)
            elif n_entries == 1:
                # TODO UPDATE here
                logger.debug('[TODO] DB Entry already exists: "%s.%s"' \
                        % (db_path, key))
            else:
                logger.warning('Multiple documents with same find query\n \
                        "%s" in "%s"' % (find_query, db_path) )

def init():
    """
    """
    init_db()

    # http://stackoverflow.com/questions/100210/python-easy-way-to-add-n-seconds-to-a-datetime-time
    sched.add_date_job( fetch_food_menu, datetime.now() + timedelta(minutes=1) )
    sched.add_date_job( fetch_general_announcements, datetime.now() + timedelta(minutes=1) )

    logger.debug('Initialization successful!')


def main():
    if not health_check():
        logger.error('Health check FAILED! Terminating...')
        sys.exit(1)

    init()

    sched.add_interval_job( fetch_food_menu, minutes=60 )
    sched.add_interval_job( fetch_general_announcements, minutes=10 )

    try:
        sched.start()
    except (KeyboardInterrupt):
        logger.debug('>> Got SIGTERM! Terminating...')


@sched.interval_schedule(minutes=10)
def fetch_courses(n_workers=1, timeout_secs=10, n_tries=3):
    """
    """
    logger.debug('Will now fetch the courses')
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


@sched.interval_schedule(minutes=10)
def fetch_uth_rss(n_workers=1, timeout_secs=10, n_tries=3):
    """
    """
    logger.debug('Will now fetch announcements')
    types = [ rss['type'] for rss in db.uth.rss.find() ]

    # Initialize a pool of 'n_workers' greenlets
    n_workers = len(types)
    worker_pool = Pool(n_workers)

    # Enqueue the tasks
    for type in types:
        worker_pool.spawn( update_rss, type, timeout_secs, n_tries )

    worker_pool.join()


if __name__ == '__main__':
    main()
