#!/usr/bin/env python
# -*- coding: utf-8 -*-

# TODO:
# Logging & Error handling

import requests
from bs4 import BeautifulSoup

import os
import re
import unicodedata
import logging


logger = logging.getLogger(__name__)


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
        logger.warning("fetch_html: connection error while fetching" +
                '\n\t' + link)
        return None
    except requests.exceptions.Timeout:
        logger.warning("fetch_html: timeout while fetching" + '\n\t' + link)
        return None

    if page.status_code is not (200 or 301):
        logger.warning("fetch_html: could not retrieve" + '\n\t' + link)
        return None

    return page.text


def html_to_disk(link, html):
    """
    store the html in a file on the disk

    http://docs.python.org/2/tutorial/inputoutput.html#reading-and-writing-files
    http://docs.python.org/2/library/functions.html#open
    """
    filename = slugify(link) + '.html'

    # create or open the file for writing
    try:
        with open(filename, 'w+') as f:
            f.write(html.encode('utf-8'))
    except Exception as e:
        print("html_to_disk: %s" % e)
        #logger.error("html_to_disk: %s" % e)
        return None

    return filename


def html_from_disk(link):
    """
    read and return the html from a file on the disk

    http://docs.python.org/2/tutorial/inputoutput.html#reading-and-writing-files
    http://docs.python.org/2/library/functions.html#open
    """
    filename = slugify(link) + '.html'

    # open the file for reading
    try:
        with open(filename, 'r') as f:
            html = f.read()
    except Exception as e:
        print("html_from_disk: %s" % e)
        #logger.error("html_from_disk: %s" % e)
        return None

    return html


def get_bsoup(html):
    """
    Create a BeautifulSoup object from html string
    """
    try:
        bsoup = BeautifulSoup(html)
    except Exception as e:
        logger.error("get_bsoup: %s" % e)

    return bsoup


def download_file(link, filename, timeout=5.0):
    """
    Download a file and save it to disk
    """
    # open the file for writting
    with open(filename, 'wb') as handle:
        try:
            # streaming the file to its location
            page = requests.get(link, timeout=timeout, stream=True)
            for block in page.iter_content(1024):
                if not block:
                    break
                handle.write(block)

        except requests.exceptions.Timeout:
            logger.warning("download_file: timeout while fetching" + '\n\t' + link)
            return None
