#!/usr/bin/env python
# -*- coding: utf-8 -*-

# TODO:
# Get proper link for courses
# Logging and testing

# asynchronous scrapping wrapper

# import gevent.monkey and apply the patch for async operations
import gevent.monkey
gevent.monkey.patch_all()

from pymongo import MongoClient
client = MongoClient()

def fetch_courses(n_workers, timeout_secs, n_tries):
    """
    """
    from courses.announcements import parsing_func
    from util import fetch_html, get_bsoup
    import gevent.queue
    import gevent.pool

    # Initialize an empty queue to hold the tasks
    task_queue = gevent.queue.Queue()

    # Initialize a pool of 'n_workers' greenlets
    worker_pool = gevent.pool.Pool(n_workers)

    # Enqueue the tasks
    for course_name in parsing_func.keys():
        task_queue.put(course_name)

    # Greenlet function
    def crawl_page():

        # Get the course name, or exit if no left in queue
        try:
            course_name = task_queue.get()
        except gevent.queue.Empty:
            return

        # Get the database
        db = client.uthportal

        # Set the query
        query = {'code': course_name.upper() }

        # Read from DB link to course
        try:
            records = db.inf.courses.find(query)

            if records.count() is 0:
                # TODO: error
                pass
            if records.count() > 1:
                # TODO: warning
                pass

            link = records[0]['announcements']['link']
            if link is None:
                # TODO: error
                pass

        except Exception as ex:
            print ex.message
            return


        # Try to fetch_html 'n_tries'
        for i in xrange(n_tries):
            html = fetch_html(link, timeout=timeout_secs)

            if html is not None:
                break
            elif i is n_tries - 1:
                return

        # Get BeautifulSoup Object
        bsoup = get_bsoup(html)
        if bsoup is None:
            return

        # Parse the html and return the data
        data = None
        try:
            data = parsing_func[course_name](bsoup)
        except Exception as ex:
            print ex.message


        # If data are valid update the db
        if data is not None:
            print course_name
            update_query = { '$set': { 'announcements.items': data  } }
            db.inf.courses.update(query, update_query)

    # Spawn workers till there are no more tasks
    while ( not task_queue.empty() ):
        # TODO
        # does this introduce a delay? if yes, can we mitigate it?
        gevent.sleep(0.1)
        #gevent.sleep(0)

        # Find the best number of workers to spawn
        n_spawns = min( task_queue.qsize(), worker_pool.free_count() )

        # Spawn 'n_spawns' workers
        for i in xrange(0, n_spawns):
            worker_pool.spawn(crawl_page)

    # Wait for all the workers to finish
    worker_pool.join()


# define a testbench function and run it if the module is run directly
if __name__ == '__main__':
    def testbench():
        data = fetch_courses(1, 10, 3)
        #print(data['ce120'][-13][0].date())
        #print(data['ce120'][-13][1])
        #print(data['ce232'][-5][0].date())
        #print(data['ce232'][-5][1])

    testbench()
