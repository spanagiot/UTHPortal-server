#!/usr/bin/env python
# -*- coding: utf-8 -*-

# parsing functions of course pages

from bs4 import BeautifulSoup
from datetime import datetime
import string

debug = False

# TODO: All functions return a list of dicts in the format:
# { 'date':date, 'html':html, 'has_time': 0/1 } 

# course parsing function dictionary
# NOTE
# a course may have more than one page with data. how do we generalize this
# dictionary? should we introduce a "course" class, that will also contain links
# and information about each course?
parsing_func = {}

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
    announce_list = list()

    # Parse each announcement
    for announce in announce_class.findAll('span', class_ = 'date'):
        # Get date, remove any unwanted punctuation and convert to datetime
        # Formats: http://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior
        date_string = announce.text.strip(string.punctuation)
        date = datetime.strptime(date_string , '%d/%m/%Y')

        # Get the parts of the announcement
        parts = list()
        for part in announce.next_siblings:
            if part.name is 'span' or part.name is 'p':
                break
            parts.append( unicode(part) )

        # Covert list to unicode
        announce_html = (''.join( parts )).strip()

        # Add the new announcement as dictionary
        announce_list.append( {'date':date, 'html':announce_html, 'has_time': False } )

    # Return the list of announcements
    return announce_list


def ce232(bsoup):
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
    return [ {'date':date, 'html':html, 'has_time': False} for (date,html) in zip(dates,contents) ]


# add the course parsing functions to the dictionary
parsing_func['ce120'] = ce120
parsing_func['ce232'] = ce232

"""
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
"""
