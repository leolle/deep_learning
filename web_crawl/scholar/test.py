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
from bs4 import BeautifulSoup

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
URL_SEARCH = config.URL_GOOGLE_SCHOLAR
PROXIES = config.PROXIES
rate_delay = 2
error_delay = 5
proxies = config.PROXIES
cookies = config.COOKIES


def get_data(filename, folder, default=''):
    root_folder = os.getcwd()
    # root_folder = os.path.dirname(__file__)
    user_agents_file = os.path.join(os.path.join(root_folder, folder), filename)
    try:
        with open(user_agents_file) as fp:
            data = [_.strip() for _ in fp.readlines()]
    except:
        data = [default]
    return data


def get_random_user_agent():
    return random.choice(get_data('user_agents.txt', 'data', USER_AGENT))


def get_random_domain():
    domain = random.choice(get_data('all_domain.txt', 'data', DOMAIN))
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
            cookies=cookies,
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
# time.sleep(pause)
domain = get_random_domain()
url = URL_SEARCH
url = url.format(
    domain=domain, query=quote_plus(query), language=language, start=start)
if language is None:
    url = url.replace('hl=None&', '')
QueryURL = req_url(query, language, start, pause=2)

# cold boot
# bsObj = Cold_boot(QueryURL)
with open('./data/all_domain.txt', 'r') as f:
    scholar_domains = f.readlines()
scholar_domains = [w.replace('\n', '') for w in scholar_domains]
r = 'a'
for domain in scholar_domains:
    try:
        headers = {'user-agent': get_random_user_agent()}
        # domain = get_random_domain()
        url = URL_SEARCH
        url = url.format(
            domain=domain,
            query=quote_plus(query),
            language=language,
            start=start)
        requests.packages.urllib3.disable_warnings(
            requests.packages.urllib3.exceptions.InsecureRequestWarning)
        r = requests.get(
            url=url,
            proxies=proxies,
            headers=headers,
            cookies=cookies,
            allow_redirects=False,
            verify=False,
            timeout=30)
        print(url)
        time.sleep(30)
    except requests.exceptions.SSLError as e:
        print(e)
        # LOGGER.info(url)
        ylog.debug(domain)
        time.sleep(30)

while r != '':
    try:
        headers = {'user-agent': get_random_user_agent()}
        domain = get_random_domain()
        url = URL_SEARCH
        url = url.format(
            domain=domain,
            query=quote_plus(query),
            language=language,
            start=start)
        requests.packages.urllib3.disable_warnings(
            requests.packages.urllib3.exceptions.InsecureRequestWarning)
        r = requests.get(
            url=url,
            proxies=proxies,
            headers=headers,
            allow_redirects=False,
            verify=False,
            timeout=30)
        time.sleep(5)
    except requests.exceptions.SSLError as e:
        print(e)
        # LOGGER.info(url)
        ylog.debug(domain)
        time.sleep(5)
        continue
LOGGER.info(url)
content = r.content
charset = cchardet.detect(content)
text = content.decode(charset['encoding'])
bsObj = BeautifulSoup(text, "lxml")

# result counts
brief_counts = bsObj.find_all('div', id='gs_ab_md')[0].text
print(brief_counts)
text1 = brief_counts.replace(r',', "")
pattern = re.compile(u'\d+')
result_count = re.findall(pattern, text1)[0]
print(result_count)

# content
global download_link
global abstarct
infomation = []

for iid in bsObj.find_all('div', class_={'gs_ri'}):
    Link = iid.find('a').attrs['href']
    print(Link)
    # Title = iid.find('h3', class_='gs_rt').text
    # print(Title)

for iid in bsObj.find_all('div', class_={'gs_r', 'gs_or', 'gs_scl'}):
    Link = iid.find('a').attrs['href']
    print(Link)
    Title = iid.find('h3', class_='gs_rt').text
    print(Title)

    if len(iid.find_all('div', class_='gs_a')) != 0:
        infos = iid.find_all('div', class_='gs_a')[0].text
        items = infos.split('-')
        if len(items) > 2:
            Author = items[0]
            print(Author)
            public = items[1]
            print(public)
            source = '-'.join(items[2:])
            print(source)
        elif len(items) == 2:
            print(items)
            Author = items[0]
            print(Author)
            public = items[1]
            print(public)
            source = None
        else:
            public = items[0]
            print(public)

    if iid.find('div', class_='gs_rs') is not None:
        abstarct = iid.find('div', class_='gs_rs').text
        print(abstarct)
    if len(iid.find_all('div', class_='gs_ggsd')) != 0:
        download_link = iid.find_all('div', class_='gs_ggsd')[0].text
        print(download_link)
    if iid.find_all('div', class_='gs_fl') is not None:
        if len(iid.find_all('div', class_='gs_fl')) == 2:
            cited = iid.find_all(
                'div', class_='gs_fl')[1].text.strip(' ').split(' ')
            pattern = re.compile(u'(\d+)')
            if len(re.findall(pattern, cited[0])) != 0:
                cited_counts = int(re.findall(pattern, cited[0])[0])
                print(cited_counts)
            else:
                cited_counts = 0

        elif len(iid.find_all('div', class_='gs_fl')) == 1:
            cited = iid.find_all(
                'div', class_='gs_fl')[0].text.strip(' ').split(' ')
            pattern = re.compile(u'(\d+)')
            if len(re.findall(pattern, cited[0])) != 0:
                cited_counts = int(re.findall(pattern, cited[0])[0])
                print(cited_counts)
            else:
                cited_counts = 0

        else:
            cited_counts = 0
    infos = {
        'Link': Link,
        'Title': Title,
        # 'Author': Author,
        # 'public': public,
        # 'source': source,
        # 'abstarct': abstarct,
        # 'download_link': download_link,
        # 'cited_counts': cited_counts
    }
    infomation.append(infos)
