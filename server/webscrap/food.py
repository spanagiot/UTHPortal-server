#!/usr/bin/env python
# -*- coding: utf-8 -*-

# TODO:
# Exception handling
# Logging actions for debugging purpuses

import re
import requests
from bs4 import BeautifulSoup
from util import download_file, get_bsoup

from os import path,makedirs
from subprocess import call
from datetime import datetime,timedelta

link = 'http://uth.gr/static/miscdocs/merimna/'
folder_name = 'food-menu/'

def _convert_to_html(doc_filepath, htm_filepath):
    """
    Uses soffice library ( used by LibreOffice & OpenOffice ) to convert
    the .doc file to the according .html one.
    
    Reference:
    https://help.libreoffice.org/Common/Starting_the_Software_With_Parameters
    """ 
    
    # set the arguments and make the call
    soffice_args = ['soffice', '--headless', '--convert-to', 'htm:HTML', '--outdir', folder_name, doc_filepath ] 
    ret_code = call(soffice_args)
    
    if ret_code == 0 and path.exists(htm_filepath):
        return True
    else:
        return False

def _prettify(text):
    """
    Strips the starting and trailing whitespaces from text as well 
    as the unecessary -multiple- whitspaces found between the words
    due to bad formating
    
    Also remove any unecessary informations.
    """
    special_menu = u'ΕΙΔΙΚΟ ΜΕΝΟΥ'
    
    pretty_text = unicode()
    is_whitespace = False
    for i in xrange(len(text)):
        if text[i].isspace() and not is_whitespace:
            # first whitespace character found after a non-whitespace one
            pretty_text += ' '
            is_whitespace = True
        elif not text[i].isspace():
            # normal character 
            pretty_text += text[i]
            is_whitespace = False
    
    # removes the 'special_menu' string from the text
    new_end = pretty_text.find(special_menu)
    if new_end is not -1:
        pretty_text = pretty_text[:new_end]
    
    return pretty_text

def _split_dishes(cell):
    """
    Split the dishes according to a pattern, which hasn't been found
    at that moment.
    
    Feel free to modify and experiment on it
    """
    
    pass

def _parse_html(html):
    """
    Feel free to propose any changes on the schema below.
    
    Dictionary format:
    
    'lunch'-> 'main'   -> unicode
              'salad'  -> unicode
              'desert' -> unicode
              
    'dinner'-> 'main'   -> unicode
               'salad'  -> unicode
               'desert' -> unicode
    """
    
    weekdays = [ 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday' ]
    
    # get the cells from the html
    bsoup = get_bsoup(html)
    cells = [ _prettify(cell.text) for cell in bsoup.find_all('td') ]
    
    # split the cells according to meal. hardcoded positions 
    lunch  = [ cells[ 9:16], cells[17:24], cells[25:32] ]
    dinner = [ cells[41:48], cells[49:56], cells[57:64] ]
    
    # create the menu dictionary
    menu = dict()
    for i in xrange(7):
        menu[ weekdays[i] ] = dict()
        menu[ weekdays[i] ]['lunch' ] = { 'main': lunch[0][i], 'salad': lunch[1][i], 'desert': lunch[2][i] }
        menu[ weekdays[i] ]['dinner'] = { 'main': dinner[0][i], 'salad': dinner[1][i], 'desert': dinner[2][i] }
    
    return menu

def fetch_menu( date=datetime.now() ):
    # calculate the first day of the week
    monday = date - timedelta(date.weekday())
    
    # filename format: 'menusitisis_YYYYMMDD'
    filename = 'menusitisis_%d%02d%02d' % (monday.year, monday.month, monday.day)
    doc_filepath = folder_name + filename + '.doc'
    htm_filepath = folder_name + filename + '.htm'
    
    # create the folder path, if necessary
    if not path.exists(folder_name):
        makedirs(folder_name)
    
    # download the doc file
    download_file(link + filename + '.doc', doc_filepath)

    if not path.exists(doc_filepath):
        return None
    
    if not _convert_to_html(doc_filepath, htm_filepath):
        return None
    
    # reads the html code from disk
    file_html = open(htm_filepath, 'r')
    html = file_html.read()
    file_html.close()
    
    try:
        food_dict = _parse_html(html)
        
        if isinstance(food_dict, dict):
            return food_dict
        
    except Exception as exception:
        print exception.message
        pass


# testing code
if __name__ == '__main__':
    weekdays = [ 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun' ]
    menu = fetch_menu(datetime.now() )
    #menu = fetch_menu(datetime(2014,1,23) )
	
    if isinstance(menu, dict):
        for day in weekdays:
            print day.upper()
            for time in menu[day]:
                print time.upper()
                print '\t#  MAIN  #: ' + menu[day][time]['main'  ]
                print '\t#  SALAD #: ' + menu[day][time]['salad' ]
                print '\t# DESERT #: ' + menu[day][time]['desert']
    else:
        print 'Error here!'

