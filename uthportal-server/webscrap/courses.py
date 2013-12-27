#!/usr/bin/env python
# -*- coding: utf-8 -*-

# this module contains functions used to scrap pages of courses residing on
# the server at inf-server.inf.uth.gr

import requests
from datetime import datetime
from bs4 import BeautifulSoup

# UTH courses server URL
courses_link = 'http://inf-server.inf.uth.gr/courses/'

# Dictionary that maps course names to functions
# Initialize as an empty dictionary
courses_func = dict()

def get_bsoup(link):
    """
    get the HTML of the page, create and return the BeautifulSoup object
    """

    # get the webpage
    webpage = requests.get(link)

    # create a BeautifulSoup object
    bsoup = BeautifulSoup(webpage.content)

    # return the BeautifulSoup object
    return bsoup

def CE120():
    """
    course: CE120 : Προγραμματισμός 1

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

    # get the BeautifulSoup object
    bsoup = get_bsoup(courses_link + 'CE120/')

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
            announce_string = announce.text[splitter+1:].strip()

            # Convert the date from string to datetime object
            # Formats: http://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior
            date = datetime.strptime(date_string, '%d/%m/%Y')

            # Add the new announcement as tuple to the list
            announce_list.append( (date, announce_string) )

    # Return the list of announcements
    return announce_list

# Add the courses to the dictionary
courses_func['CE120'] = CE120

# define a testbench function and run it if the module is run directly
if __name__ == '__main__':
    def testbench():
        announcements = CE120()
        for (date, text) in announcements:
            print(date)
            print(text.encode('utf-8') + '\n')

    testbench()
