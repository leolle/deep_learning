# -*- coding: utf-8 -*-
"""
Created on Wed May  9 11:36:42 CST 2018
@author: Wei Wu
"""

import os
import random
import time
import re
import cchardet
import requests
from math import ceil
from pyquery import PyQuery as pq

import logging
from urllib.parse import quote_plus, urlparse, parse_qs
from deep_learning.web_crawl.config import LOGGER
from ylib import ylog
from ylib.yaml_config import Configuraion

ylog.set_level(logging.DEBUG)
ylog.console_on()
ylog.filelog_on("app")

logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)
config = Configuraion()

config.load('../config.yaml')
USER_AGENT = config.USER_AGENT
DOMAIN = config.DOMAIN
BLACK_DOMAIN = config.BLACK_DOMAIN
URL_SEARCH = config.URL_GOOGLE_SEARCH
PROXIES = config.PROXIES
rate_delay = 2
error_delay = 5
proxies = config.PROXIES


def get_data(filename, default=''):
    root_folder = os.getcwd()
    # root_folder = os.path.dirname(__file__)
    user_agents_file = os.path.join(os.path.join(root_folder, 'data'), filename)
    try:
        with open(user_agents_file) as fp:
            data = [_.strip() for _ in fp.readlines()]
    except:
        data = [default]
    return data


def get_random_user_agent():
    return random.choice(get_data('user_agents.txt', USER_AGENT))


def get_random_domain():
    domain = random.choice(get_data('all_domain.txt', DOMAIN))
    if domain in BLACK_DOMAIN:
        get_random_domain()
    else:
        return domain


def req_url(query, language=None, start=0, pause=2):
    time.sleep(pause)
    domain = get_random_domain()
    url = URL_SEARCH
    url = url.format(
        domain=domain, query=quote_plus(query), language=language, start=start)
    if language is None:
        url = url.replace('hl=None&', '')
    return url


def Cold_boot(url, pause=3):

    headers = {'user-agent': get_random_user_agent()}
    try:
        requests.packages.urllib3.disable_warnings(
            requests.packages.urllib3.exceptions.InsecureRequestWarning)
        r = requests.get(
            url=url,
            proxies=proxies,
            headers=headers,
            allow_redirects=False,
            verify=False,
            timeout=30)
        time.sleep(pause)
        LOGGER.info(url)
        content = r.content
        charset = cchardet.detect(content)
        bsObj = content.decode(charset['encoding'])
        return bsObj
    except (ValueError, Exception) as e:
        print(e.message)
        print("Sleeping for %i" % error_delay)
        time.sleep(error_delay)
        return Cold_boot(url)


def filter_link(link):
    try:
        o = urlparse(link, 'http')
        if o.netloc:
            return link
        if link.startswith('/url?'):
            link = parse_qs(o.query)['q'][0]
            o = urlparse(link, 'http')
            if o.netloc:
                return link
    except Exception as e:
        LOGGER.exception(e)
        return None


query = 'china'
nums = 10
language = 'en'
start = 0
pause = 2

# gain data
global PageURL
time.sleep(pause)
domain = get_random_domain()
url = URL_SEARCH
url = url.format(
    domain=domain, query=quote_plus(query), language=language, start=start)
if language is None:
    url = url.replace('hl=None&', '')
QueryURL = req_url(query, language, start, pause=2)

# cold boot
# bsObj = Cold_boot(QueryURL)
r = ''
while r == '':
    try:
        headers = {'user-agent': get_random_user_agent()}
        requests.packages.urllib3.disable_warnings(
            requests.packages.urllib3.exceptions.InsecureRequestWarning)
        r = requests.get(
            url=url,
            proxies=proxies,
            headers=headers,
            allow_redirects=False,
            verify=False,
            timeout=30)
        time.sleep(3)
    except:
        print('exception')
        time.sleep(pause)
        continue
LOGGER.info(url)
content = r.content
charset = cchardet.detect(content)
bsObj = content.decode(charset['encoding'])
# pq html
try:
    pq_content = pq(bsObj)
    # return init_content
except ValueError:
    LOGGER.exception(ValueError)
# content
result = []
if pq_content is not None:
    for item in pq_content('div.g').items():
        information = {'Title': None, 'PageURL': None, 'Abstract': None}
        Title = item('h3.r>a').eq(0).text()
        href = item('h3.r>a').eq(0).attr('href')
        if href:
            PageURL = filter_link(href)

        MatchedAbstract = item('span.st').text()
        information = {
            'Title': Title,
            'PageURL': PageURL,
            'MatchedAbstract': MatchedAbstract
        }
        result.append(information)

# TotalCount = counts_result(bsObj, start)
# RelatedKeywords = search_relation(bsObj, pause=2)
# pages = int(ceil(nums / 20))
# page = 0
# Allinformations = []
# while page < pages:
#     print(page)
#     start = page * 20
#     url = req_url(query, language, start, pause=2)
#     print(url)
#     bsObj = Cold_boot(url)
#     info = content(bsObj)
#     print(len(info))
#     if len(info) == 0:
#         break
#     Allinformations = Allinformations + info
#     page = page + 1
# infos = {
#     'Query': query,
#     'TotalCount': TotalCount,
#     'QueryURL': QueryURL,
#     'RelatedKeywords': RelatedKeywords,
#     'Allinformations': Allinformations
# }
