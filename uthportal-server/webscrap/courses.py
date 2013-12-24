#!/usr/bin/env python
# -*- coding: utf-8 -*-

from BeautifulSoup import BeautifulSoup, Tag
import requests

# UTH Server courses URL #
coursesLink = 'http://inf-server.inf.uth.gr/courses/'

########################################################################
# Returns the BeautifulSoup HTML Tree
########################################################################
def GetTree(link):
    # Download the webpage #
    webpage = requests.get( coursesLink + 'CE120/' )

    # Parse the HTML code into DOM using BeautifulSoup #
    tree = BeautifulSoup( webpage.content );

    # Return the tree #
    return tree

########################################################################
# COURSE     :    CE120 -> Προγραμματισμός Ι
# HTML FORMAT:    <div class="announce">
#                     <p>
#                     <span class="date"> #date1# </span> #announce1#
#                     </p>
#                     <p>
#                     <span class="date"> #date2# </span> #announce2#
#                     </p>
#                     ...
#                 </div>
# RETURN     :    List of tuples: [ (date1,announce1) , ... ]
########################################################################
def CE120():
    # Get the HTML tree #
    tree = GetTree(coursesLink + 'CE120/')

    # Find announce class #
    # tree.find( tag_name , attributes ) #
    announce_class = tree.find('div', attrs = {'class':'announce'} )

    # Parse the dates and create the list #
    date_elements = announce_class.findAll('span', attrs = {'class':'date'} );
    date_list = [ date.text[:-1] for date in date_elements ]

    # Parse the announcements and create the list #
    text_elements = announce_class.findAll('p');
    text_list = list()

    for element in text_elements:
        if len(element.text) > 0:
            text = unicode()
            for block in element.contents[2:]:
                if type(block) == Tag: # Tag -> BeautifulSoup.Tag #
                    text += block.text
                else:
                    text += block

            text_list.append( text.strip() )

    # Return the tuples #
    return [ (date,text) for (date,text) in zip( date_list, text_list) ]


## Testbench ##
#announcement = CE120();
#for (date,text) in announcement:
#    print date
#    print text + '\n'
