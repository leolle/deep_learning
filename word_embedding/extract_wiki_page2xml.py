#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
import sys, os.path
import re, random
import argparse
from itertools import izip
import logging, traceback
import urllib
import bz2, gzip
from htmlentitydefs import name2codepoint
import Queue, threading, multiprocessing
import pandas as pd

ls_pages = pd.read_csv(
    '/home/weiwu/share/deep_learning/data/finance_pages_level_5_uni.csv',
    header=None).iloc[:, 1].values

# Program version
version = '2.9'

# ----------------------------------------------------------------------
# READER

tagRE = re.compile(r'(.*?)<(/?\w+)[^>]*>(?:([^<]*)(<.*?>)?)?')

#tagRE = re.compile(r'(.*?)<(/?\w+)[^>]*>([^<]*)')
#                    1     2            3


def process_data(input_file, ids, templates=False):
    """
    :param input_file: name of the wikipedia dump file.
    :param ids: article ids (single or range first-last).
    :param templates: collect also templates
    """

    if input_file.lower().endswith("bz2"):
        opener = bz2.BZ2File
    else:
        opener = open

    input = opener(input_file)
    print '<mediawiki>'

    rang = ids.split('-')
    first = int(rang[0])
    if len(rang) == 1:
        last = first
    else:
        last = int(rang[1])
    page = []
    curid = 0
    for line in input:
        line = line.decode('utf-8')
        if '<' not in line:  # faster than doing re.search()
            if page:
                page.append(line)
            continue
        m = tagRE.search(line)
        if not m:
            continue
        tag = m.group(2)
        if tag == 'page':
            page = []
            page.append(line)
            inArticle = False
        elif tag == 'id' and not curid:  # other <id> are present
            curid = int(m.group(3))
            if first <= curid <= last:
                page.append(line)
                inArticle = True
            elif curid > last and not templates:
                break
            elif not inArticle and not templates:
                page = []
        elif tag == 'title':
            if templates:
                if m.group(3).startswith('Template:'):
                    page.append(line)
                else:
                    page = []
            else:
                page.append(line)
        elif tag == '/page':
            if page:
                page.append(line)
                print ''.join(page).encode('utf-8')
                if not templates and curid == last:
                    break
            curid = 0
            page = []
        elif page:
            page.append(line)

    print '</mediawiki>'
    input.close()


def main():
    parser = argparse.ArgumentParser(
        prog=os.path.basename(sys.argv[0]),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=__doc__)
    parser.add_argument("input", help="XML wiki dump file")
    parser.add_argument(
        "--id", default="", help="article number, or range first-last")
    parser.add_argument(
        "--template", action="store_true", help="extract also all templates")
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version='%(prog)s ' + version,
        help="print program version")

    args = parser.parse_args()

    process_data(args.input, args.id, args.template)


xml_file = '/home/weiwu/share/deep_learning/data/enwiki-20170820-pages-articles.xml.bz2'
process_data(xml_file, '55970164')
