#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Pan Yang (panyangnlp@gmail.com)
# Copyright 2017

import string
from tqdm import tqdm
from sys import stdin
import codecs
import sys
import fileinput
import logging

logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

PY2 = sys.version_info[0] == 2

if PY2:
    from itertools import izip as zip, izip_longest as zip_longest
    range = xrange  # Use Python 3 equivalent
    chr = unichr  # Use Python 3 equivalent
    text_type = unicode

else:
    from itertools import zip_longest
    text_type = str


def pages_from(input_file):
    """
    Scans input extracting pages.
    :return: (id, revid, title, namespace key, page), page is a list of lines.
    """
    page = []
    for line in input_file:
        if not isinstance(line, text_type):
            line = line.decode('utf-8')
            page.append(line)


def load_templates(input_file, output_file=None):
    """
    Load templates from :param file:.
    :param output_file: file where to save templates and modules.
    """
    if output_file:
        output = codecs.open(output_file, 'wb', 'utf-8')
    for page_count, page_data in enumerate(pages_from(input_file)):
        output.write(page_data)


input_file = './data/zhwiki-latest-categorylinks.zhs.sql'
full_path = '/home/weiwu/share/deep_learning/data/zhwiki_cat_pg_lk/zhwiki-latest-categorylinks.sql'
# with open(input_file, 'r') as f:
#     for i, line in enumerate(f):
#         if not isinstance(line, text_type):
#             line = line.decode('utf-8')
#         print(line)
import linecache
import re, os, time
# theline = linecache.getline(full_path, 963)
start = 963
end = 963
batch_size = 200
total_line_size = 1593
with open(full_path, 'rb') as f:
    try:
        for i, line in enumerate(tqdm(f)):
            if i >= start and i <= end:
                print("line #: %s/%s" % (i, total_line_size))
                line = line.decode('utf-8')
                try:
                    last_span = re.search(line).span()[0]
                except AttributeError:
                    continue
                line_size = len(re.findall(line))
                for _ in tqdm(range(0, line_size, batch_size)):
                    # pause if find a file naed pause at the currend dir
                    while os.path.isfile('pause'):
                        time.sleep(100)
                        print("pause for 100 second")
                    re_batch = {}
                    for j in range(batch_size):
                        re_batch[j] = re.search(line, last_span)
                        if re_batch[j] is not None:
                            last_span = re_batch[j].span()[1]
            elif i > end:
                break
    except UnicodeDecodeError as e:

        last_span = e.start + 10
        line = line[last_span:].decode('utf-8')
        try:
            last_span = re.search(line).span()[0]
        except AttributeError:
            continue
        line_size = len(re.findall(line))
        for _ in tqdm(range(0, line_size, batch_size)):
            # pause if find a file naed pause at the currend dir
            re_batch = {}
            for j in range(batch_size):
                re_batch[j] = re.search(line, last_span)
                if re_batch[j] is not None:
                    last_span = re_batch[j].span()[1]
        # print(line)
        # for
        #         re_batch[j] = re.search(line, last_span)
        #         if re_batch[j] is not None:
        #             last_span = re_batch[j].span()[1]
        #     func(re_batch)
