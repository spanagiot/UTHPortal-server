#!/usr/bin/env python
# -*- coding: utf-8 -*-

# TODO:
# Exception Handling
# Write document file for HTML format

import requests
from bs4 import BeautifulSoup

def fetch_course_links():
    link = 'http://www.inf.uth.gr/cced/?page_id=16'
    
    # get the undergraduate course page
    page = requests.get(link)
    if page.status_code is not 200:
        return None
    
    # find the table containing all courses
    bsoup = BeautifulSoup(page.content)
    main_table = bsoup.find('table', attrs={'class':'outer_undergraduate_program'})
    
    # get all courses links
    links = [ cell['href'] for cell in main_table.find_all('a',href=True) ]
    return links

def fetch_course_info(link):
    
    # get the course page defined by the link
    page = requests.get(link)
    if page.status_code is not 200:
        return None
    
    # get the regions we are interested in
    bsoup = BeautifulSoup(page.content)
    header = bsoup.find('header', attrs={'id':'page-heading'})
    table = bsoup.find('table', class_='course')
    
    # create the dict and get the name of the course
    info = dict()
    info['name'] = header.find('h1').text
    
    # find (if exists) if the course has a dedicated page
    info['link'] = unicode()
    cell_url = table.find('th',text=u'Σελίδα Μαθήματος')
    if cell_url is not None:
        info['link'] = cell_url.find_next_sibling('td').a['href']
        
    return info


# testing code
if __name__ == '__main__':
    links_list = fetch_course_links()
    #links_list = [ 'http://www.inf.uth.gr/cced/?page_id=1553' ]
    
    courses_info = dict()
    for link in links_list:
        info = fetch_course_info(link)
        
        if isinstance(info, dict):
            print info['name'] + ': ' + info['link']
        
            
        
