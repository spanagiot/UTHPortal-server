#!/usr/bin/env python
# -*- coding: utf-8 -*-

# parsing functions of course pages

from util import slugify, fetch_html

from bs4 import BeautifulSoup
from datetime import datetime

debug = False

# course parsing function dictionary
# NOTE
# a course may have more than one page with data. how do we generalize this
# dictionary? should we introduce a "course" class, that will also contain links
# and information about each course?
courses_func = {}

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

    # get the html of the page
    html = fetch_html('http://inf-server.inf.uth.gr/courses/CE120/')

    # create a BeautifulSoup object
    bsoup = BeautifulSoup(html)

    # find the 'announce' class which contains the announcements
    # bsoup.find(tag_name, attributes)
    announce_class = bsoup.find('div', class_ = 'announce')

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


# testing code to be run when the module is run directly
# NOTE
# should all tests be off the file/module to be tested?
if __name__ == '__main__':
    debug = True

    ce120_announcements = ce120()
    ce232_announcements = ce232()

    def print_all(announcements):
        for (date, content) in announcements:
            print(date.date())
            print(content)
            print('')

    def print_single(announcements, index):
        print(announcements[index][0].date())
        print(announcements[index][1])

    #print_all(ce120_announcements)
    print_single(ce120_announcements, -13)

    #print_all(ce232_announcements)
    print_single(ce232_announcements, -5)
