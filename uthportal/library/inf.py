#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Department of Electrical and Computer Engineering

# parsing functions for announcements of the department and information and
# announcements of the department's courses

import logging
import requests
import string
from util import parse_greek_date
from bs4 import BeautifulSoup, Tag
from datetime import datetime
from util import fetch_html, get_bsoup
from pymongo import MongoClient

logger = logging.getLogger(__name__)

client = MongoClient()
# Get the database
db = client.uthportal

### info.py ###################################################################

# TODO:
# Exception Handling
# Write document file for HTML format

def fetch_course_links():
    """
    """
    link = 'http://www.inf.uth.gr/cced/?page_id=16'

    # get the html from the undergraduate course page
    html = fetch_html(link)
    bsoup = get_bsoup(html)

    # find the table containing all courses
    main_table = bsoup.find('table', attrs={'class':'outer_undergraduate_program'})

    # get all courses links
    links = [ cell['href'] for cell in main_table.find_all('a',href=True) ]
    return links


def fetch_course_info(link):
    """
    """
    # get the html from the course page defined by the link
    html = fetch_html(link)
    bsoup = get_bsoup(html)

    # get the regions we are interested in
    header = bsoup.find('header', attrs={'id':'page-heading'})
    table = bsoup.find('table', class_='course')

    # create the dict and get the name of the course
    info = {}
    info['name'] = header.find('h1').text

    # find (if exists) if the course has a dedicated page
    info['link'] = u''
    cell_url = table.find('th',text=u'Σελίδα Μαθήματος')
    if cell_url is not None:
        info['link'] = cell_url.find_next_sibling('td').a['href']

    return info


def update_course_info(info):
    """
    """
    pass

### /info.py ##################################################################


### announcements.py ##########################################################

# parsing functions of course announcement pages

# NOTE
# all functions return a list of dicts in the format:
# { 'date':date, 'html':html, 'has_time': 0/1 }
# NOTE
# shouldn't the format be:
# { 'date':date, 'time': time/None, 'html':html }
# or even:
# { 'date':date, 'time': time/None, 'link':link, 'html':html }

def ce120(bsoup):
    """
    course: ce120 : Προγραμματισμός 1

    HTML format:
        <div class="announce">
            <p>
            <span class="date"> #date1# </span> #announce1#
            </p>
            <p>
            <span class="date"> #date2# </span> #announce2#
            </p>
            ...
        </div>
    """

    # find the 'announce' class which contains the announcements
    # bsoup.find(tag_name, attributes)
    announce_class = bsoup.find('div', class_ = 'announce')

    # Initialize an empty list
    announce_list = []

    # Parse each announcement
    for announce in announce_class.find_all('span', class_ = 'date'):
        # Get date, remove any unwanted punctuation and convert to datetime
        # Formats: http://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior
        date_string = announce.text.strip(string.punctuation)
        date = datetime.strptime(date_string , '%d/%m/%Y')

        # Get the parts of the announcement
        html_parts = []
        plaintext_parts = []
        for part in announce.next_siblings:
            if part.name is 'span' or part.name is 'p':
                break

            html_parts.append( part.encode('utf8'))
            if hasattr(part, 'text'):
                plaintext_parts.append( part.text.strip() )
            else:
                plaintext_parts.append( part )

        # convert list to unicode
        html = (''.join( html_parts )).strip()
        plaintext = (''.join( plaintext_parts )).strip()

        # Add the new announcement as dictionary
        announce_list.append( {'date':date, 'html':html, 'plaintext': plaintext, 'has_time': False } )

    # Return the list of announcements
    return announce_list


def ce121(bsoup):
    """
    course 121: Προγραμματισμος ΙΙ

    HTML Format:

    <a id="announce"></a>
    <h3>Ανακοινωσεις</h3>
    <ul class="nb">
	    <li><b>date1 <span style="color:#C00000"> title1 </span> </b><br>
	        <ul class="nb">
 		        <li> html1
		        </li>
	        </ul>
	    </li>
	    <li><b>date2 <span style="color:#C00000"> title2 </span> </b><br>
	        <ul class="nb">
 		        <li> html2
		        </li>
	        </ul>
	    </li>
    </ul>
    """
    # Get the region of the announcements
    announce_region = bsoup.find('a', id='announce')

    # Move to the ul tag
    announce_region = announce_region.find_next_sibling()
    announce_region = announce_region.find_next_sibling()

    # Find all b inside li (dates & titles)
    dates_titles = announce_region.select('li > b')

    # Find all announcements html
    htmls = announce_region.find_all('ul', class_='nb')

    # Remove the ul 'outer' tag and create the plaintext entry
    plaintexts = [ ]
    for (i, html) in enumerate(htmls):
        plaintexts.append(html.text.strip())
        html = unicode(html).replace('<ul class="nb">', '')
        html = unicode(html).replace('</ul>', '')
        htmls[i] = html

    # Create the final list
    announce_list = [ {'title': element.span.extract().text.encode('utf8'), \
                        'date': datetime.strptime(element.text.strip(), '%d/%m/%Y'), 'has_time': False, \
                        'html': htmls[i].encode('utf8').strip(), \
                        'plaintext': plaintexts[i] } for (i, element) in enumerate(dates_titles) ]

    return announce_list

def ce134(bsoup):
    return ce232(bsoup)

def ce213(bsoup):
    """
    Course: HΥ213 Αριθμητική Ανάλυση

    HTML Format:

    <li>
       <h3> <font color="#669933">date1. </font></h3>
        <p> html1
        </p>
    </li>

    <li>
       <h3> <font color="#669933">date2. </font></h3>
       <p> html2
       </p>
    </li>
    ....
    """
    # Find all html announcement
    htmls = bsoup.select('li h3 ~ p')

    # Find all dates
    dates = bsoup.select('li h3 > font')
    dates = [ datetime.strptime(date.text.strip(' .'), '%d/%m/%Y') \
                for date in dates ]

    return [ { 'date':date, 'html': html.encode('utf8'), 'has_time': False, \
            'plaintext': html.text.strip() } for (date, html) in zip(dates, htmls) ]


def ce230(bsoup):
    """
    Course: ΗΥ230 Ανάλυση Κυκλωμάτων
    """
    return ce232(bsoup)

def ce232(bsoup):
    """
    course: ΗΥ232 Οργάνωση και Σχεδίαση Ηλεκτρονικών Υπολογιστών

    HTML format:
        <h1>
        Ανακοινώσεις
        </h1>

        <!-- begin content area -->
        <dt> <b> date1 </b> </dt>
        <dd> announcement1 </dd>
        </dl>
        <br/>

        <dt> <b> date2 </b> </dt>
        <dd> announcement2 </dd>
        </dl>
        <br/>

        ...

        <!-- end content area -->
    """
    # create a list of the announcement dates
    dates_raw = [date.find('b').text.strip() for date in bsoup.find_all('dt')]
    # using a list comprehension, see
    # http://docs.python.org/2/tutorial/datastructures.html#list-comprehensions
    # date.find('b') : get the html code from the descendant b tag of date
    # http://www.crummy.com/software/BeautifulSoup/bs4/doc/#find
    # bsoup.find_all('dt') : get a list with the html code from all descendants
    # dt tag of bsoup
    # http://www.crummy.com/software/BeautifulSoup/bs4/doc/#find-all

    # create datetime objects from the date strings
    # http://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior
    dates = [datetime.strptime(date, '%d/%m/%Y') for date in dates_raw]

    contents = []
    plaintexts = []

    # create a list of the announcement html contents
    dd_contents = bsoup.find_all('dd')
    for dd_elements in dd_contents:
        content = u''
        plaintext = u''
        for element in dd_elements:
            content += unicode(element)

            if hasattr(element, 'text'):
                plaintext += element.text
            else:
                plaintext += unicode(element)

        contents.append( content.strip() )
        plaintexts.append( plaintext )

    # return the date/content tuples
    return [ {'date':date, 'html':html, 'plaintext': plaintext, 'has_time': False} \
                                    for (date, html, plaintext) in zip(dates, contents, plaintexts) ]

def ce321(bsoup):
    """
    course: ce321 : Λειτουργικα Συστηματα
    HTML format:
    <span class="date"> #date1# </span> #announce1#
    <span class="date"> #date2# </span> #announce2#
    ...
    """

    for announce in find_all('span', 'color:#'):
        # Get date, remove any unwanted punctuation and convert to datetime
        date_string = announce.text.strip(string.punctuation)
        date = datetime.strptime(date_string, '%d/%m/%Y')
        parts = []

        # Get the parts of the announcement
        for parts in announce.next_sibling:
            parts.append(unicode(part))

        # convert list to unicode
        announce_html = (''.join( parts )).strip()

        # Add the new announcement as dictionary
        announce_list.append( {'date':date, 'html':announce_html, 'has_time': False } )

    # Return the list of announcements
    return announce_list

def ce420(bsoup):
    """
    Course: HY420 Σχεδίαση και Ανάπτυξη Λογισμικού
    """
    return ce120(bsoup)

def ce431(bsoup):
    """
    Course: Αρχιτεκτονική Παράλληλων Συστημάτων
    """
    return ce232(bsoup)

def ce536(bsoup):
    """
    Course: Εργαστήριο Αναλογικών Συστημάτων VLSI
    """
    dates = [datetime.strptime(date_element.text.strip(), '%d/%m/%Y') for date_element in bsoup.select('dt > b')]
    htmls = [ann_element.encode('utf8') for ann_element in bsoup.select('dt + dd')]
    titles = [ann_element.text.strip() for ann_element in bsoup.select('dt + dd')]
    return [ {'date': date, 'html': html, 'plaintext': title, 'has_time': False} \
                                    for (date, html, title) in zip(dates, htmls, titles) ]

def ce538(bsoup):
    """
    Course: Αρχιτεκτονική Παράλληλων Συστημάτων
    """
    return ce232(bsoup)

def update_course(code, timeout_secs, n_tries):
    # Set the query
    query = {'code': code }

    # Read from DB link to course
    try:
        records = db.inf.courses.find(query)

        if records.count() is 0:
            logger.error('[%s] No entry found' % code)
            return False

        if records.count() > 1:
            logger.warning('[%s] Multiple entries found' % code)

        link = records[0]['announcements']['link']
        if link is None:
            logger.warning('[%s] Course does not have "link" field' % code)
            return False

    except Exception as ex:
        logger.warning('[%s] %s' % (code, ex) )
        return False

    logger.debug('[%s] Fetching course' % code)
    # Try to fetch_html 'n_tries'
    for i in xrange(n_tries):
        html = fetch_html(link, timeout=timeout_secs)

        if html is not None:
            break
        elif i is n_tries - 1:
            return False

    logger.debug('[%s] Getting BeautifulSoup object' % code)
    # Get BeautifulSoup Object
    try:
        bsoup = get_bsoup(html)
        if bsoup is None:
            return False
    except Exception as ex:
        logger.warning('[%s] %s' % (code, ex) )
        return False

    logger.debug('[%s] Trying to parse...' % code)
    # Parse the html and return the data
    try:
        parser = globals()[code]
        data = parser(bsoup)
    except Exception as ex:
        logger.warning('[%s] %s' % (code, ex) )
        return False

    # Add the 'title' entry when is not already
    # NOTE: If title entry is not present then title
    # is set as COURSE-CODE - DATE-OF-ANNOUNCEMENT
    try:
        for entry in data:
            if 'title' not in entry:
                entry['title'] = '%s - %s' % (code.upper(), \
                        entry['date'].strftime('%2d/%2m/%4Y'))
    except Exception as ex:
        logger.warning('[%s] %s' % (code, ex) )
        return False

    logger.debug('[%s] Updating database...' % code)
    # If data are valid update the db
    if data is not None:
        try:
            # Update the announcements & last_updated
            site_update_query = { '$set': { 'announcements.site': data } }
            date_update_query = { '$set': { 'announcements.last_updated': datetime.now() } }
            db.inf.courses.update(query, site_update_query)
            db.inf.courses.update(query, date_update_query)
        except Exception as ex:
            logger.warning('[%s] %s' % (code, ex) )
            return False

    logger.debug('[%s] Successfull run!' % code)
    return True

### /announcements.py #########################################################

def announcements_general(bsoup):
    """
    general announcements

    http://www.inf.uth.gr/cced/?cat=24

    HTML format:
        <div id="post">
            <article>

                <div class="loop-entry-right">
                    <h2><a href="" title=""></a></h2>

                    [content]

                </div>

                <div class="loop-entry-left">
                    <div class="post-meta">
                        <div class="post-date">

                           [date]

                        </div>
                    </div>
                </div>

            </article>

            ...

            <div class="page-pagination clearfix">
                <span class="current">1</span>
                <a href=''>2</a>
                <a href=''>3</a>
                <a href=''>4</a>
            </div>
        </div>
    """
    #initialize announcement list
    announcements = []

    # get post containining announcements
    posts = bsoup.find(id='post')

    # get articles from post
    articles =  posts.find_all('article', class_='loop-entry clearfix')

    #loop thorugh articles
    for article in articles:
        #initialize announcement dictionary
        announcement = {}

        # get left part
        left = article.find('div', class_='loop-entry-left')
        date_post = left.find('div', class_= 'post-meta').find('div', class_ = 'post-date')
        announcement['date'] = parse_greek_date( date_post.text )

        #get right part
        right = article.find('div', class_='loop-entry-right')

        announcement['title'] = right.h2.a['title']
        announcement['link'] = right.h2.a['href']

        paragraphs = right.find_all( 'p' )

        #join all paragraps to a single html
        announcement['html'] = '\n'.join( [unicode(p) for p in paragraphs] )

        # get the plaintext from html
        bsoup = get_bsoup(announcement['html'])
        announcement['plaintext'] = bsoup.text.strip()

        #add to announcements
        announcements.append( announcement )


    return announcements

def announcements_graduates():
    """
    graduates announcements
    http://www.inf.uth.gr/cced/?cat=5
    """
    pass

def fetch_general_announcements():
    type = 'genannounce'

    # Set the query
    query = { 'type' : type }

    try:# Read from DB links
        records = db.inf.announce.find(query)

        if records.count() is 0:
            logger.error('[%s] No document found' % type)
            return False

        if records.count() > 1:
            logger.warning('[%s] Multiple documents found' % type)

        link = records[0]['link']
        if link is None:
            logger.warning('[%s] Document does not have "link" field' % type)
            return False
    except Exception as ex:
        logger.warning('[%s] %s' % (type, ex))
        return False

    logger.debug('Fetching announcements...')
    try:
        html = fetch_html(link)
        if html is None:
            logger.warning('[%s] Empty HTML' % type)
            return

    except Exception as ex:
        logger.warning('[%s] %s' % (type, ex))
        return

    bsoup = get_bsoup(html)
    if bsoup is None:
        return

    try:
        ann_list = announcements_general(bsoup)
    except Exception as ex:
        logger.warning('[%s] %s' % (type, ex))
        return

    # Create the dictionary
    db_doc = { }
    db_doc['entries'] = ann_list
    db_doc['last_updated'] = datetime.now()

    # Update the database
    find_query = { 'type' : type }
    update_query = { '$set' : db_doc }

    try:
        db.inf.announce.update(find_query, update_query)
    except Exception as ex:
        logger.error('[%s] %s' % (type, ex))


### testing code

def test_fetch_course_links():
    """
    """
    links_list = fetch_course_links()
    #links_list = [ 'http://www.inf.uth.gr/cced/?page_id=1553' ]

    courses_info = {}
    for link in links_list:
        info = fetch_course_info(link)

        if isinstance(info, dict):
            print(info['name'] + ':' +
                    info['link'])

### /testing code

if __name__ == '__main__':
    """
    """
    test_announcements()
    #fetch_general_announcements()
