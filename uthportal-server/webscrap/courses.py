#!/usr/bin/env python
# -*- coding: utf-8 -*-

# parsing functions of course pages

from bs4 import BeautifulSoup
from datetime import datetime
import os
import re
import requests
import unicodedata

# course parsing function dictionary
# NOTE
# a course may have more than one page with data. how do we generalize this
# dictionary? should we introduce a "course" class, that will also contain links
# and information about each course?
courses_func = {}


def slugify(value):
    """
    convert to lowercase, remove non valid characters (alphanumeric, dot,
    dash, and underscore), convert spaces to hyphens, and strip leading
    and trailing whitespace.

    initially copied from
    https://github.com/django/django/blob/master/django/utils/text.py
    since customized to own specifications
    """
    value = unicode(value)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = value.decode('ascii')

    # replace characters using regular expressions
    # http://docs.python.org/2/library/re.html
    value = re.sub('[^\w\s\.-]', '_', value).strip().lower()
    value = re.sub('_+', '_', value).strip('_')
    value = re.sub('[-\s]+', '-', value)
    return value


def fetch_html(link):
    """
    fetch the html of the page, store it on the disk, return it as a string

    http://docs.python.org/2/tutorial/inputoutput.html#reading-and-writing-files
    http://docs.python.org/2/library/functions.html#open

    NOTE
    maybe add an option to store the html in the database

    NOTE
    should the string be a unicode one?
    """

    filename = slugify(link) + '.html'

    # if we are debugging and the file with the page html exists on the disk
    if debug and os.path.exists(filename):
        # open the file as read-only
        f = open(filename, 'r')
        # get the html from the file
        html = f.read()
    else:
        # fetch the page
        page = requests.get(link)
        # TODO
        # error checking

        # store the page on the disk
        # open or create the file for writing
        f = open(filename, 'w+')
        html = page.content
        f.write(html)

    # close the file
    f.close()

    # return the html string
    return html


def ce120():
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

    return:
    list of tuples: [(date1, announce1), ...]
    """
    #print __name__

    # get the html of the page
    html = fetch_html('http://inf-server.inf.uth.gr/courses/CE120/')

    # create a BeautifulSoup object
    bsoup = BeautifulSoup(html)

    # find the 'announce' class which contains the announcements
    # bsoup.find(tag_name, attributes)
    announce_class = bsoup.find('div', attrs = {'class':'announce'})

    # Initialize an empty list
    announce_list = list()

    # Parse each announcement (which lies inside a <p> tag)
    for announce in announce_class.findAll('p'):
        if announce.text.strip(): # announcement not empty
            # Find when the date splits from the actual announcement
            splitter = announce.text.find(':')

            # Get the date and the announcement as strings
            date_string = announce.text[:splitter].strip()
            announce_string = announce.text[splitter+1:].encode('utf-8').strip()

            # Convert the date from string to datetime object
            # Formats: http://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior
            date = datetime.strptime(date_string, '%d/%m/%Y')

            # Add the new announcement as tuple to the list
            announce_list.append( (date, announce_string) )

    # Return the list of announcements
    return announce_list


def ce232():
    """
    course: ce232 : Computer Organization and Design

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

    return:
    list of tuples: [(date1, announce1), ...]
    """

    # get the html of the page
    html = fetch_html('http://inf-server.inf.uth.gr/courses/CE232/')

    # create a BeautifulSoup object
    bsoup = BeautifulSoup(html)

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
        content = ''
        for element in dd_elements:
            content += element.encode('utf-8')
        contents.append( content.strip() )

    # return the date/content tuples
    return zip(dates, contents)


# add the course scrapping functions to the dictionary
courses_func['ce120'] = ce120
courses_func['ce232'] = ce232


# define a testbench function and run it if the module is run directly
if __name__ == '__main__':
    def testbench():
        announcements = CE120()
        for (date, text) in announcements:
            print(date.date())
            print(text + '\n')

    #testbench()

    def test_ce232():
        announcements = ce232()
        for (date, content) in announcements:
            print(date.date())
            print(content)
            print('')

    #test_ce232()
