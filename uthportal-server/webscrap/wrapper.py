# Import gevent.monkey and apply
# the patch for async operations
import gevent.monkey
gevent.monkey.patch_all()

def fetch_courses(n_workers, timeout_secs, n_tries):
    import courses
    import gevent.queue
    import gevent.pool

    # Initialize an empty queue to hold the tasks
    task_queue = gevent.queue.Queue()

    # Initialize a pool of 'n_workers' greenlets
    worker_pool = gevent.pool.Pool(n_workers)

    # Initialize a dict that holds results from greenlets
    # { name_of_course:data_fetched , ... }
    courses_data = dict()

    # Initialize an error message dictionary
    error_messages = dict()

    # Enqueue the tasks
    for func in courses.courses_func.values():
        task_queue.put(func)

    # Greenlet function
    def crawl_page():
        # If there are no other jobs
        # NOTE: May be overkill
        if task_queue.empty():
            return

        # Get the function that need to call
        func = task_queue.get()

        success = False # Was the job successfull?
        error_list = list()

        # Try to fetch data 'n_tries' times
        for i in xrange(0,n_tries):

            # Set the timeout
            timeout = gevent.Timeout(timeout_secs)
            timeout.start()

            try:
                # Call the function to receive the data
                data = func()

                # If something went wrong data is set to None
                if(data is not None):
                    success = True

            except Timeout: # Timout exception
                error_list.append('[%d] Timeout error: %lf secs' % (i,timeout_secs) )
            except Exception as ex: # Other exception
                error_list.append(ex.message)
            finally:
                timeout.cancel()

            # If the call was successfull
            if success:
                courses_data[func.__name__] = data
            else:
                print error_list
                #error_messages[func.__name__] = error_list

    # Spawn workers till there are no more tasks
    while( not task_queue.empty() ):
        gevent.sleep(0.1)

        # Find the best number of workers to spawn
        n_spawns = min( task_queue.qsize(), worker_pool.free_count() )

        # Spawn 'n_spawns' workers
        for i in xrange(0, n_spawns):
            worker_pool.spawn(crawl_page)

    # Wait for all the workers to finish
    worker_pool.join()

    return courses_data

# define a testbench function and run it if the module is run directly
if __name__ == '__main__':
    def testbench():
        data = fetch_courses(1,10,3)
        print data['CE120'][0][1]

    testbench()
