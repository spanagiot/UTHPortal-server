#!/usr/bin/env python
# -*- coding: utf-8 -*-

# this module contains functions used to scrap pages of courses residing on
# the server at inf-server.inf.uth.gr

import requests
from datetime import datetime
from bs4 import BeautifulSoup

# UTH courses server URL
courses_link = 'http://inf-server.inf.uth.gr/courses/'

def get_soup(link):
    """
    get the HTML of the page, create and return the BeautifulSoup object
    """

    # download the webpage
    webpage = requests.get(link)

    # create a BeautifulSoup object
    soup = BeautifulSoup(webpage.content)

    # return the soup
    return soup


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

    # get the soup
    soup = get_soup(courses_link + 'CE120/')

    # find the 'announce' class which contains the announcements 
    # soup.find(tag_name, attributes)
    announce_class = soup.find('div', attrs = {'class':'announce'})
    
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
            date = datetime.strptime(date_string,'%d/%m/%Y')
            
            # Add the new announcement as tuple to the list
            announce_list.append( (date,announce_string) ) 
            
    # Return the list of announcements 
    return announce_list

### testbench
announcements = CE120()
for (date, text) in announcements:
    print(date)
    print(text + '\n')
