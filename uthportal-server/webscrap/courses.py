#!/usr/bin/env python
# -*- coding: utf-8 -*-

# this module contains functions used to scrap pages of courses residing on
# the server at inf-server.inf.utf.gr

import requests
from bs4 import BeautifulSoup, Tag

# UTH courses server URL
courses_link = 'http://inf-server.inf.uth.gr/courses/'

def get_soup(link):
    """
    get the HTML of the page, create and return the BeautifulSoup object
    """

    # download the webpage
    webpage = requests.get(courses_link + 'CE120/')

    # fix encoding issue
    webpage.encoding = 'utf-8'

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
    list of tuples: [(date1, announce1) , ...]
    """

    # get the soup
    soup = get_soup(courses_link + 'CE120/')

    # find the class announce
    # soup.find(tag_name, attributes)
    announce_class = soup.find('div', attrs = {'class':'announce'})

    # parse the dates and create the list
    date_elements = announce_class.findAll('span', attrs = {'class':'date'})
    date_list = [date.text[:-1] for date in date_elements]

    # parse the announcements and create the list
    text_elements = announce_class.findAll('p')
    text_list = list()

    for element in text_elements:
        if len(element.text) > 0:
            text = unicode()
            for block in element.contents[2:]:
                if type(block) == Tag: # Tag -> BeautifulSoup.Tag
                    text += block.text
                else:
                    text += block

            text_list.append(text.strip())

    # return the tuples
    return [(date, text) for (date, text) in zip(date_list, text_list)]


### testbench
announcement = CE120()
for (date, text) in announcement:
    print(date)
    print(text + '\n')
