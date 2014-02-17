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


def fetch_html(link, timeout=8.0):
    """
    fetch and return the html of a page as a unicode string
    """
    try:
        page = requests.get(link, timeout=timeout)
    except requests.exceptions.ConnectionError:
        #logging.error("fetch_html: connection error while fetching" +
        #        '\n\t' + link)
        return None
    except requests.exceptions.Timeout:
        #logging.error("fetch_html: timeout while fetching" + '\n\t' + link)
        return None

    if page.status_code is not (200 or 301):
        #logging.error("fetch_html: could not retrieve" + '\n\t' + link)
        return None

    # TODO
    # return the html as a unicode string
    # currently it's a simple string
    return page.content

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
