# -*- coding: utf-8 -*-
"""
Created on Wed May  9 11:36:42 CST 2018
@author: Wei Wu
crawl google scholar using beautiful soup 4
"""
import os
import random
import sys
import time
import re
import cchardet
import requests
#import pandas as pd
# import bs4
from bs4 import BeautifulSoup
# from pandas import DataFrame
from math import ceil
# import config
# from config import USER_AGENT, URL_SEARCH, URL_NEXT, LOGGER
from deep_learning.web_crawl.config import LOGGER
import logging
from urllib.parse import quote_plus, urlparse, parse_qs
from ylib import ylog
from ylib.yaml_config import Configuraion

ylog.set_level(logging.DEBUG)
ylog.console_on()
ylog.filelog_on("app")

logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)
config = Configuraion()

config.load('/home/weiwu/projects/deep_learning/web_crawl/config.yaml')
USER_AGENT = config.USER_AGENT
DOMAIN = config.DOMAIN
BLACK_DOMAIN = config.BLACK_DOMAIN
URL_SEARCH = config.URL_GOOGLE_SCHOLAR
URL_NEXT = config.URL_GOOGLE_SCHOLAR_NEXT
PROXIES = config.PROXIES
COOKIES = config.COOKIES
if sys.version_info[0] > 2:
    from urllib.parse import quote_plus, urlparse, parse_qs
else:
    from urllib import quote_plus
    from urlparse import urlparse, parse_qs


class Scholar():
    """
    scholar google search.
    """

    def __init__(self, rate_delay=2, error_delay=5, proxies=PROXIES):

        self.rate_delay = rate_delay
        self.error_delay = error_delay
        self.proxies = proxies

    def get_random_user_agent(self):
        return random.choice(self.read_file('user_agents.txt', USER_AGENT))

    def get_random_domain(self):
        domain = random.choice(self.read_file('all_domain.txt', DOMAIN))
        if domain in BLACK_DOMAIN:
            self.get_random_domain()
        else:
            return domain

    def counts_result(self, bsObj):
        """count the total results number from scholar searching"""

        try:
            breif_counts = bsObj.find_all('div', id='gs_ab_md')[0].text
            text1 = breif_counts.replace(r',', "")
            pattern = re.compile(u'\d+')
            result_count = re.findall(pattern, text1)[0]
            # print(result_count)
        except IndexError:
            result_count = 0
        except AttributeError:
            result_count = 0
        return result_count

    def content(self, bsObj, pause=2):
        global download_link
        global abstarct
        infomation = []
        try:
            outputs = bsObj.find_all('div', class_={'gs_r', 'gs_or', 'gs_scl'})
        except AttributeError:
            return []
        for iid in outputs:
            Link = iid.find('a').attrs['href']
            # print(Link)
            Title = iid.find('h3', class_='gs_rt').text
            # print(Title)

            if len(iid.find_all('div', class_='gs_a')) != 0:
                infos = iid.find_all('div', class_='gs_a')[0].text
                items = infos.split('-')
                if len(items) > 2:
                    Author = items[0]
                    # print(Author)
                    public = items[1]
                    # print(public)
                    source = '-'.join(items[2:])
                    # print(source)
                elif len(items) == 2:
                    # print(items)
                    Author = items[0]
                    # print(Author)
                    public = items[1]
                    # print(public)
                    source = None
                else:
                    public = items[0]
                    # print(public)

#                    print '*'*30

            if iid.find('div', class_='gs_rs') is not None:
                abstarct = iid.find('div', class_='gs_rs').text
                # print(abstarct)
            if len(iid.find_all('div', class_='gs_ggsd')) != 0:
                download_link = iid.find_all('div', class_='gs_ggsd')[0].text
                # print(download_link)
            if iid.find_all('div', class_='gs_fl') is not None:
                if len(iid.find_all('div', class_='gs_fl')) == 2:
                    cited = iid.find_all(
                        'div', class_='gs_fl')[1].text.strip(' ').split(' ')
                    pattern = re.compile(u'(\d+)')
                    if len(re.findall(pattern, cited[0])) != 0:
                        cited_counts = int(re.findall(pattern, cited[0])[0])
                        # print(cited_counts)
                    else:
                        cited_counts = 0

                elif len(iid.find_all('div', class_='gs_fl')) == 1:
                    cited = iid.find_all(
                        'div', class_='gs_fl')[0].text.strip(' ').split(' ')
                    pattern = re.compile(u'(\d+)')
                    if len(re.findall(pattern, cited[0])) != 0:
                        cited_counts = int(re.findall(pattern, cited[0])[0])
                        # print(cited_counts)
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

        return infomation

    def req_url(self, query, language=None, start=0, pause=2):
        time.sleep(pause)
        #        domain = ''
        domain = self.get_random_domain()
        if start > 0:
            url = URL_NEXT
            url = url.format(
                domain=domain, query=quote_plus(query), start=start)
        else:

            url = URL_SEARCH
            url = url.format(
                domain=domain, query=quote_plus(query), language=language)
        return url

    def Cold_boot(self, url, pause=2):

        time.sleep(pause)
        headers = {'user-agent': self.get_random_user_agent()}
        try:
            requests.packages.urllib3.disable_warnings(
                requests.packages.urllib3.exceptions.InsecureRequestWarning)
            r = requests.get(
                url=url,
                proxies=self.proxies,
                headers=headers,
                cookies=COOKIES,
                allow_redirects=False,
                verify=False,
                timeout=30)
            logging.info(url)
            content = r.content
            charset = cchardet.detect(content)
            text = content.decode(charset['encoding'])
            bsObj = BeautifulSoup(text, "lxml")
            return bsObj
        except requests.exceptions.SSLError as e:
            logging.exception(e)
            return None


#        else: Exception as e:
        else:
            logging.exception('request error')
            return None

    def get_random_user_agent(self):
        """
        Get a random user agent string.
        :return: Random user agent string.
        """
        return random.choice(self.read_file('user_agents.txt', USER_AGENT))

    def get_related_keywords(self, bs_obj):
        """get related keywords in the infomation output.
        bs_obj -- beautiful soup object
        """
        try:
            suggests = bs_obj.find_all("div", id="gs_qsuggest")[-1]
            a_bf = BeautifulSoup(str(suggests), 'lxml')
            a = a_bf.find_all('a')
            return [gs_li.get_text() for gs_li in a]
        except IndexError:
            return []
        except AttributeError:
            return []

    def gain_data(self, query, language=None, nums=None, pause=5):
        start = 0
        url = self.req_url(query, language, start, pause=2)
        bsObj = self.Cold_boot(url)
        related_keywords = self.get_related_keywords(bsObj)
        total_count = self.counts_result(bsObj)
        pages = int(ceil(nums / 10))
        page = 0
        all_info = []
        while page < pages:
            # print(page)
            start = page * 10
            url = self.req_url(query, start, pause=pause)
            print(url)
            bsObj = self.Cold_boot(url)
            info = self.content(bsObj, pause=pause)
            all_info = all_info + info
            page = page + 1
        infos = {
            'total_count': total_count,
            'url': url,
            'all_info': all_info,
            'related_keywords': related_keywords
        }

        return infos

    def read_file(self, filename, default=''):
        """
        Get data from a file
        :param filename: filename
        :param default: default value
        :return: data
        """
        # root_folder = os.path.dirname(__file__)
        root_folder = os.getcwd()
        user_agents_file = os.path.join(
            os.path.join(root_folder, 'data'), filename)
        try:
            with open(user_agents_file) as fp:
                data = [_.strip() for _ in fp.readlines()]
        except:
            data = [default]
        return data

if __name__ == '__main__':
    scholar = Scholar()
    data = scholar.gain_data('china', nums=10, pause=5)

# scholar = Scholar()
# data = scholar.gain_data('nlp python', language='en', nums=10, pause=5)
import networkx as nx
import copy
import random
depth = 3
# pause = random.randint(5, 30)
graph = nx.DiGraph()
base_nodes = []
end_nodes = []
i = 0
new_kw = 'entity linking'
gs = Scholar()
data = gs.gain_data(new_kw, language='en', nums=10, pause=5)

base_nodes = data['related_keywords']
logging.debug('base nodes %s' % base_nodes)

#related_keywords = data['RelatedKeywords']
for kw in base_nodes:
    # base_nodes.append(kw)
    graph.add_edge(new_kw, kw)
# logging.debug(base_nodes)

while i < depth:
    for index, b in enumerate(base_nodes):
        # if b not in graph:
        if len(graph.out_edges(b)) == 0:
            logging.info('crawling: %s' % b)
            data = gs.gain_data(
                query=b, language='en', nums=10, pause=random.randint(15, 30))
            nodes = data['related_keywords']
            if not nodes:
                continue
            # logging.debug('%s is already in graph' % b)
        else:
            nodes = []
        logging.debug("new nodes: %s" % nodes)
        end_nodes.extend(nodes)
        if len(nodes) > 0:
            for n in nodes:
                graph.add_edge(b, n)
    base_nodes = copy.copy(end_nodes)
    logging.info('level %s nodes: %s' % (i, end_nodes))
    end_nodes = []
    i += 1
nx.write_gexf(graph, new_kw + ".gexf")
