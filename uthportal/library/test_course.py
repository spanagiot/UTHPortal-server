from inf import *
from util import fetch_html, get_bsoup
from pymongo import MongoClient

code = 'ce121'
n_tries = 3
timeout_secs = 10

client = MongoClient()
db = client.uthportal

if __name__ == '__main__':
    def print_dict():
        # Set the query
        query = {'code': code }

        # Read from DB link to course
        try:
            records = db.inf.courses.find(query)

            if records.count() is 0:
                print '[%s] No entry found' % code
                return False

            if records.count() > 1:
                print '[%s] Multiple entries found' % code

            link = records[0]['announcements']['link']
            if link is None:
                print '[%s] Course does not have "link" field' % code
                return False

        except Exception as ex:
            print '[%s] %s' % (code, ex)
            return False

        print '[%s] Fetching course' % code
        # Try to fetch_html 'n_tries'
        for i in xrange(n_tries):
            html = fetch_html(link, timeout=timeout_secs)

            if html is not None:
                break
            elif i is n_tries - 1:
                return False

        print '[%s] Getting BeautifulSoup object' % code
        # Get BeautifulSoup Object
        try:
            bsoup = get_bsoup(html)
            if bsoup is None:
                return False
        except Exception as ex:
            print '[%s] %s' % (code, ex)
            return False

        print '[%s] Trying to parse...' % code
        # Parse the html and return the data
        try:
            parser = globals()[code]
            data = parser(bsoup)
        except Exception as ex:
            print '[%s] %s' % (code, ex)
            return False

        # Print the data
        for item in data:
            for key in item:
                val = item[key]
                if isinstance(val, basestring):
                    val = val.decode('utf8')
                else:
                    val = unicode(val)

                print '%s: %s' % (key, val)
            print '\n'

    print_dict()

