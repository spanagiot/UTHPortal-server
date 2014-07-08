#!/usr/bin/env python
# -*- coding: utf-8 -*-

# University of Thessaly

import logging
import feedparser

from datetime import datetime
from time import mktime
from pymongo import MongoClient
from util import fetch_html, get_bsoup

logging.basicConfig()
logging.level = logging.DEBUG
logger = logging.getLogger(__name__)

# Get the database
client = MongoClient()
db = client.uthportal

def normalize_rss(entries):
    """
    Module for normalizing rss feeds from uth.gr

    Description field of rss in uth.gr contains the title too.
    We remove the title from description
    """
    for entry in entries:
        bsoup = get_bsoup(entry['html'])
        # Remove unwanted data
        bsoup.strong.extract()
        bsoup.div.extract()

        entry['html'] = bsoup
        entry['plaintext'] = bsoup.text.strip()

        # Encode the values
        for key in [ 'html', 'plaintext' ]:
            entry[key] = entry[key].encode('utf8')

    return entries

def update_rss(type, timeout_secs, n_tries):
    # Set the query
    query = { 'type' : type }

    try:# Read from DB links
        records = db.uth.rss.find(query)

        if records.count() is 0:
            logger.error('[%s] No document found' % type)
            return False

        if records.count() > 1:
            logger.warning('[%s] Multiple documents found' % type)

        link = records[0]['link']
        link_suffix = records[0]['link_suffix']
        if link is None:
            logger.warning('[%s] Document does not have "link" field' % type)
            return False
        if link_suffix is None:
            logger.warning('[%s] Document does not have "link_suffix" field' % type)
            return False

        # Update the link
        link = link + link_suffix
    except Exception as ex:
        logger.warning('[%s] %s' % (type, ex))
        return False


    logger.debug('[%s] Fetching RSS file' % type)
    # Try to fetch_html 'n_tries'
    for i in xrange(n_tries):
        html = fetch_html(link, timeout=timeout_secs)

        if html is not None:
            break
        elif i is n_tries - 1:
            return False


    logger.debug('[%s] Parsing RSS ...' % type)
    # Trying to parse rss from html
    try:
        rss = feedparser.parse(html)
    except Exception as ex:
        logger.error('[%s] %s' % (type, ex))
        return False
    else:
        if rss is None:
            logger.warning('[%s] Empty RSS dictionary')
            return False

        # Datetime format
        # dt_format = '%a, %d %b %Y %H:%M:%S %z'

        # Create rss dict we need
        entries = [ {'title': entry.title, 'html': entry.description, 'plaintext': u'', \
                'date': datetime.fromtimestamp(mktime(entry.published_parsed)) } for entry in rss.entries ]

    # Prettify/normalize rss
    try:
        n_entries = normalize_rss(entries)
    except Exception as ex:
        logger.error('[%s] %s' % (type, ex))
    else:
        if n_entries is None:
            logger.warning('[%s] Normalized failed', type)

        logger.debug('[%s] Normalized successfull!', type)
        entries = n_entries # Replace with n(ormalized)_entries

    try:
        entries_update_query = { '$set': { 'entries' : entries } }
        date_update_query = { '$set' : { 'last_updated' : datetime.now() } }

        db.uth.rss.update(query, entries_update_query)
        db.uth.rss.update(query, date_update_query)
    except Exception as ex:
        logger.warning('[%s] %s' % (type, ex))
        return False
    else:
        logger.debug('[%s] Successfull update!' % type)

    return True

"""
if __name__ == '__main__':
    entries = update_rss('news', 10, 3)

    for entry in entries:
        print 'title: ' + entry['title']
        print 'desc : ' + entry['html']
        print 'plaintext: ' + entry['plaintext']
        print 'datetime: %s' % entry['date']
"""
