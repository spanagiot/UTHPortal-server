#!/usr/bin/env python
# -*- coding: utf-8 -*-

# TODO:
# Logging & Error handling

import requests
from bs4 import BeautifulSoup

import os
import re
import unicodedata

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


def fetch_html(link, timeout=5.0):
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

    # logging python class way better!
    """
    # if we are debugging and the file with the page html exists on the disk
    if debug and os.path.exists(filename):
        # open the file as read-only
        with open(filename, 'r') as f:
            # get the html from the file
            html = f.read()
    else:
    """

    # fetch the page
    try:
        page = requests.get(link, timeout=timeout)
    except requests.exceptions.Timeout:
        # TODO: Logging
        return None

    if page.status_code is not 200:
        return None

    # store the page on the disk
    # open or create the file for writing
    with open(filename, 'w+') as f:
        html = page.content
        f.write(html)

    # return the html string
    return html

def get_bsoup(html):
    # TODO: Error handling

    try:
        bsoup = BeautifulSoup(html)
    except:
        pass

    return bsoup

def download_file(link, filename, timeout=5.0):
    # open the file
    with open(filename, 'wb') as handle:
        try:
            # streaming the file to its location
            page = requests.get(link, timeout=timeout, stream=True)
            for block in page.iter_content(1024):
                if not block:
                    break
                handle.write(block)

        except requests.exceptions.Timeout:
            # TODO: Logging
            return None
