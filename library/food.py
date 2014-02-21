#!/usr/bin/env python
# -*- coding: utf-8 -*-

# TODO:
# Exception handling
# Logging actions for debugging purpuses

import requests
from bs4 import BeautifulSoup
from util import download_file
from pymongo import MongoClient
from pymongo.errors import OperationFailure

from os import path,makedirs
from subprocess import call
from datetime import datetime, timedelta

weekdays = [ 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday' ]
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

    if ret_code is 0 and path.exists(htm_filepath):
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

    pretty_text = u''
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

    # get the cells from the html
    bsoup = BeautifulSoup(html)
    cells = [ _prettify(cell.text) for cell in bsoup.find_all('td') ]

    # split the cells according to meal. hardcoded positions
    lunch  = [ cells[ 9:16], cells[17:24], cells[25:32] ]
    dinner = [ cells[41:48], cells[49:56], cells[57:64] ]

    # create the menu dictionary
    menu = {}
    for i in xrange(7):
        menu[ weekdays[i] ] = {}
        menu[ weekdays[i] ]['lunch' ] = { 'main': lunch[0][i], 'salad': lunch[1][i], 'desert': lunch[2][i] }
        menu[ weekdays[i] ]['dinner'] = { 'main': dinner[0][i], 'salad': dinner[1][i], 'desert': dinner[2][i] }

    return menu

def _date_to_datetime(date):
    """
    Converts date object to datetime, supported by MongoDB
    """
    return datetime.combine(date, datetime.min.time() )

def _update_database(food_menu_dict, week):
    """
    Connects to the database and stores the food_menu_dict.
    """
    week = _date_to_datetime(week)

    # Get the collection from db
    client = MongoClient()
    collection = client.uthportal.uth.food_menu

    # Queries for the 'food_menu' document (latest)
    find_query = { 'name' : 'food_menu' }
    update_query = { '$set': { 'date': week, 'menu' : food_menu_dict } }

    # Update if needed the 'food_menu' document
    document = collection.find_one(find_query)
    if not isinstance(document, dict):
        collection.update( find_query, update_query, upsert=True)
    elif document['date'] < week:
        collection.update( find_query, update_query )

    # Queries for the 'h_food_menu' (history)
    h_find_query = { 'name' : 'h_food_menu' }
    h_update_query = { '$set' : { week.isoformat() : { 'date' : week, 'menu' : food_menu_dict } } }

    # Updates the history
    collection.update(h_find_query, h_update_query, upsert=True)


def fetch_food_menu( date=datetime.today() ):
    # calculate the first day of the week
    monday = (date - timedelta(date.weekday())).date()

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
        food_menu_dict = _parse_html(html)
        for (i,day) in enumerate(weekdays):
            date_ = monday + timedelta(days=i)
            food_menu_dict[day]['date'] = _date_to_datetime(date_)

    except Exception as exception:
        print exception.message
        return None

    try:
        _update_database(food_menu_dict, monday)
    except OperationFailure:
        # TODO: Logging
        print 'AAA'
        pass

    return food_menu_dict


# testing code
if __name__ == '__main__':
    menu = fetch_food_menu(datetime(year=2014, month=1, day=23))

    """
    if isinstance(menu, dict):
        for day in weekdays:
            print day.upper()
            print menu[day]['date']
            for time in menu[day]:
                if isinstance(menu[day][time], dict):
                    print time.upper()
                    print '\t#  MAIN  #: ' + menu[day][time]['main'  ]
                    print '\t#  SALAD #: ' + menu[day][time]['salad' ]
                    print '\t# DESERT #: ' + menu[day][time]['desert']
    else:
        print 'Error here!'
    """
