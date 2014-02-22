#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Department of Electrical and Computer Engineering

# parsing functions for announcements of the department and information and
# announcements of the department's courses

import requests
from bs4 import BeautifulSoup
from bs4 import Tag
from datetime import datetime
import string


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

# course parsing functions dictionary
parsers = {}

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
        parts = []
        for part in announce.next_siblings:
            if part.name is 'span' or part.name is 'p':
                break
            parts.append( unicode(part) )

        # convert list to unicode
        announce_html = (''.join( parts )).strip()

        # Add the new announcement as dictionary
        announce_list.append( {'date':date, 'html':announce_html, 'has_time': False } )

    # Return the list of announcements
    return announce_list


def ce121(bsoup):
    """
    course 121: Προγραμματισμος ΙΙ

    HTML Format:
        <h3>Ανακοινώσεις</h3>
        <ul>
            <li><b>date1 <span ... > title1 </b>
            announce1
            </li>
            <li><b>date2 <span ... > title2 </b>
            announce2
            </li>
            ....
        </ul>
    """
    # Get the region of the announcements
    announce_region = bsoup.find('h3',text=u'Ανακοινώσεις')

    # Reach the 'ul' tag
    while True:
        if announce_region is not None and \
            getattr(announce_region, 'name') is not None and \
            announce_region.name == 'ul':
                break

        announce_region = announce_region.next_sibling

    # Parse the announcements
    announce_list = []
    for announce in announce_region.children:
        if isinstance(announce, Tag):
            # Parse the date
            date_splitter = announce.text.find(' ')
            date_string = announce.text[:date_splitter]
            date = datetime.strptime(date_string, '%d/%m/%Y')

            # Remove the date part from announcement
            html = unicode(announce)
            date_position = html.find(date_string)
            html = html[:date_position] + html[date_position + len(date_string):]

            #Add the announcement into the list
            announce_list.append( {'date':date, 'html':html, 'has_time': False} )

    return announce_list


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

    # create a list of the announcement html contents
    dd_contents = bsoup.find_all('dd')
    for dd_elements in dd_contents:
        content = u''
        for element in dd_elements:
            content += element.encode('utf-8')
        contents.append( content.strip() )

    # return the date/content tuples
    return [ {'date':date, 'html':html, 'has_time': False} for (date, html) in zip(dates,contents) ]


# add the course parsing functions to the dictionary
parsers['ce120'] = ce120
parsers['ce121'] = ce121
parsers['ce232'] = ce232

### /announcements.py #########################################################


def announcements_general():
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
    pass


def announcements_graduates():
    """
    graduates announcements
    http://www.inf.uth.gr/cced/?cat=5
    """
    pass


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
            print(info['name'].encode('utf-8') + ': ' +
                    info['link'].encode('utf-8'))


if __name__ == '__main__':
    """
    """
    test_fetch_course_links()
