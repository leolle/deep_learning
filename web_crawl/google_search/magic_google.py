# -*- coding: utf-8 -*-
import os
import random
import sys
import time
import re
import cchardet
import requests
from math import ceil
from pyquery import PyQuery as pq
# from config import USER_AGENT, DOMAIN, BLACK_DOMAIN, URL_SEARCH, LOGGER
from deep_learning.web_crawl.config import LOGGER
# from deep_learning.web_crawl.config import USER_AGENT, DOMAIN, BLACK_DOMAIN, URL_SEARCH, LOGGER

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
URL_SEARCH = config.URL_GOOGLE_SEARCH
PROXIES = config.PROXIES

# LOGGER = config.LOGGER


class MagicGoogle():
    """
    Magic google search.
    pseudo code:
    1. initialization, set rate delay, error delay, proxies
    2. gain data

    """

    def __init__(self, rate_delay=2, error_delay=5, proxies=PROXIES):

        # PROXIES = [{
        #     'http': 'http://192.168.1.126:1080',
        #     'https': 'http://192.168.1.126:1080'
        # }]

        self.rate_delay = rate_delay
        self.error_delay = error_delay
        self.proxies = proxies

    def counts_result(self, bsObj, start):
        try:
            pq_content = self.pq_html(bsObj)
            # logging.debug(pq_content)
            if pq_content is not None:
                m = pq_content('div.sd')[0].text
                if start == 0:
                    pattern = re.compile(u'(\d+)')
                    result_count = int(''.join(re.findall(pattern, m)))
                    return result_count
                else:
                    pattern = re.compile(u'(\d+)')
                    result_count = int(''.join(re.findall(pattern, m)[1:]))
                    return result_count
        except IndexError:
            return None

    def content(self, bsObj):
        """
        to parse content from bsObj, which is got from requests.get(url)
        """
        global PageURL
        pq_content = self.pq_html(bsObj)
        result = []
        if pq_content is not None:
            for item in pq_content('div.g').items():
                information = {'Title': None, 'PageURL': None, 'Abstract': None}
                Title = item('h3.r>a').eq(0).text()
                href = item('h3.r>a').eq(0).attr('href')
                if href:
                    PageURL = self.filter_link(href)

                Abstract = item('span.st').text()
                information = {
                    'Title': Title,
                    'PageURL': PageURL,
                    'Abstract': Abstract
                }
                result.append(information)
        return result

    def gain_data(self, query, nums, language=None, start=0, pause=5):
        """

        """
        global PageURL
        QueryURL = self.req_url(query, language, start, pause)
        bsObj = self.Cold_boot(QueryURL)
        TotalCount = self.counts_result(bsObj, start)
        RelatedKeywords = self.search_relation(bsObj, pause)
        # every page has 10 articles
        pages = int(ceil(nums / 20))
        page = 0
        Allinformations = []
        while page < pages:
            # print(page)
            start = page * 10
            url = self.req_url(query, language, start, pause=2)
            # print(url)
            bsObj = self.Cold_boot(url)
            info = self.content(bsObj)
            # print(len(info))
            if len(info) == 0:
                break
            Allinformations = Allinformations + info
            page = page + 1
        infos = {
            'Query': query,
            'TotalCount': TotalCount,
            'QueryURL': QueryURL,
            'related_keywords': RelatedKeywords,
            'Allinformations': Allinformations
        }
        return infos

    def get_related_keywords(self, query, nums, language=None, start=0,
                             pause=5):
        #        global m
        #        print (m)
        #        m=self.m
        global PageURL
        QueryURL = self.req_url(query, language, start, pause=pause)
        # print(QueryURL)
        bsObj = self.Cold_boot(QueryURL)
        RelatedKeywords = self.search_relation(bsObj, pause=pause)
        return RelatedKeywords

    def search_relation(self, bsObj, pause=2):

        # RelatedKw = []
        pq_content = self.pq_html(bsObj)
        # ylog.info(pq_content)
        related_str = (str(pq_content))
        related_str_re = re.compile("\"rfs\":\[[^!]+\]")
        try:
            related_str_rfs = related_str_re.search(related_str).group()
        except AttributeError:
            LOGGER.debug(related_str)
            return None
        # ylog.debug(related_str_rfs)
        related_ls_re = re.compile("(:\[|,)(\"[A-Za-z\s\u4e00-\u9fa5]*\")")
        ls_related = related_ls_re.findall(related_str_rfs)
        RelatedKw = [x[1][1:-1] for x in ls_related]
        ylog.debug(RelatedKw)
        # if pq_content is not None:
        #     for item in pq_content('p._Bmc').items():
        #         href = item('a').attr('href')
        #         if href:
        #             o = urlparse(href, 'http')
        #             if o.netloc:
        #                 kw = href
        #             if href.startswith('/search?'):
        #                 href = parse_qs(o.query)['q'][0]
        #                 o = urlparse(href, 'http')
        #                 if o.path:
        #                     kw = href
        #             RelatedKw.append(kw)
        return RelatedKw

    def req_url(self, query, language=None, start=0, pause=2):
        """
        add searching query, language, start to domain, get url
        """
        time.sleep(pause)
        domain = self.get_random_domain()
        url = URL_SEARCH
        url = url.format(
            domain=domain,
            query=quote_plus(query),
            language=language,
            start=start)
        if language is None:
            url = url.replace('hl=None&', '')
        return url

    def Cold_boot(self, url, pause=3):
        """
        retry if errors are met
        """
        headers = {'user-agent': self.get_random_user_agent()}
        try:
            requests.packages.urllib3.disable_warnings(
                requests.packages.urllib3.exceptions.InsecureRequestWarning)
            r = requests.get(
                url=url,
                proxies=self.proxies,
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
            # print('something')
            print(e.message)
            print("Sleeping for %i" % self.error_delay)
            time.sleep(self.error_delay)
            return self.Cold_boot(url)

    def filter_link(self, link):
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

    def pq_html(self, bsObj):
        try:
            init_content = pq(bsObj)
            return init_content
        except ValueError:
            LOGGER.exception(ValueError)
            return None

    def get_random_user_agent(self):
        return random.choice(self.read_file('user_agents.txt', USER_AGENT))

    def get_random_domain(self):
        domain = random.choice(self.read_file('all_domain.txt', DOMAIN))
        if domain in BLACK_DOMAIN:
            self.get_random_domain()
        else:
            return domain

    def read_file(self, filename, default=''):
        root_folder = os.path.dirname(__file__)
        # root_folder = os.getcwd()
        user_agents_file = os.path.join(
            os.path.join(root_folder, 'data'), filename)
        try:
            with open(user_agents_file) as fp:
                data = [_.strip() for _ in fp.readlines()]
        except:
            data = [default]
        return data


if __name__ == '__main__':
    mg = MagicGoogle()
    data = mg.gain_data(query='china', language='en', nums=10)
    # ylog.debug(data)
    # from pws import Google
    # from pws import Bing

    # ylog.debug(
    # Google.search(query='hello world', num=5, start=2, country_code="es"))

    # print(Bing.search('hello world', 5, 2))
# related_keywords = [
#     'china wiki', 'republic of china', 'china government', 'china flag',
#     'china military', 'china economy', 'china map'
# ]
# mg = MagicGoogle()
# for kw in related_keywords:
#     data = mg.gain_data(query=kw, language='en', nums=10)
