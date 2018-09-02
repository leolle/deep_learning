# -*- coding: utf-8 -*-
import os
import random
import time
import re
import cchardet
import requests
from math import ceil
from pyquery import PyQuery as pq
from config import USER_AGENT, DOMAIN, BLACK_DOMAIN, URL_SEARCH, LOGGER
from urllib.parse import quote_plus, urlparse, parse_qs
from bs4 import BeautifulSoup
from bs4.element import Tag
from ylib import ylog
import logging

ylog.set_level(logging.DEBUG)
ylog.console_on()
ylog.filelog_on("app")


class MagicGoogle_News():
    """
    Magic Google_News search.
    """

    def __init__(self, rate_delay=2, error_delay=5):

        PROXIES = [{
            'http': 'http://192.168.1.126:1080',
            'https': 'http://192.168.1.126:1080'
        }]

        self.rate_delay = rate_delay
        self.error_delay = error_delay
        self.proxies = random.choice(PROXIES)

    def counts_result(self, bsObj, start):

        pq_content = self.pq_html(bsObj)
        m = pq_content('div.sd')[0].text
        if start == 0:
            pattern = re.compile(u'(\d+)')
            result_count = int(''.join(re.findall(pattern, m)))
            return result_count
        else:
            pattern = re.compile(u'(\d+)')
            result_count = int(''.join(re.findall(pattern, m)[1:]))
            return result_count

    def content(self, bsObj):
        pq_content = BeautifulSoup(bsObj, "lxml")
        result = []
        # ylog.debug(pq_content)
        papers = pq_content.find_all('div', class_='g')
        for item in papers:
            information = {
                'Title': None,
                'PageURL': None,
                'text': None,
                'source': None,
                'time': None
            }
            # try:
            #print('something')
            pub_info = item.find('div', class_='slp').find_all('span')
            pub, hyphen, datetime = list(map(Tag.get_text, pub_info))
            Title = BeautifulSoup(str(item.find('h3')), "lxml").get_text()
            PageURL = item.find('a')['href']
            MatchedAbstract = item.find('div', class_='st').get_text()
            ylog.debug(Title)
            # if href:
            #     PageURL = self.filter_link(href)
            #     # print PageURL

            # MatchedAbstract = item('div.st')[0].text
            # # print MatchedAbstract
            # source = item('span.f')[0].text.split('-')
            # if len(source) > 2:
            #     PageSourceWebsite = ''.join(source[:-1])
            #     # print PageSourceWebsite
            #     a = source[-1]
            #     CreatedTime = self.clear_time(a)
            #     # print CreatedTime

            # else:
            #     PageSourceWebsite = ''.join(source[0])
            #     # print PageSourceWebsite
            #     a = source[-1]
            #     CreatedTime = self.clear_time(a)
            #     # print CreatedTime

            information = {
                'Title': Title,
                'PageURL': PageURL,
                'MatchedAbstract': MatchedAbstract,
                'CreatedTime': datetime
            }

            result.append(information)
        return result

    def gain_data(self, query, language=None, start=0, nums=0, pause=2):
        """first get articles count, then loop pages"""
        init_url = self.req_url(query, language, start, pause=2)
        bsObj = self.Cold_boot(init_url)
        # TotalCount = self.counts_result(bsObj, start)
        pages = int(ceil(nums / 10))
        page = 0
        Allinformations = []
        while page <= pages:
            print(page)
            start = page * 10
            url = self.req_url(query, language, start, pause=2)
            print(url)
            bsObj = self.Cold_boot(url)
            print(type(bsObj))
            info = self.content(bsObj)
            if len(info) == 0:
                break
            Allinformations = Allinformations + info
            page = page + 1
        infos = {
            # 'TotalCount': TotalCount,
            'QueryURL': init_url,
            'Allinformations': Allinformations
        }
        return infos

    def clear_time(self, time_date):
        import time
        timeclean = None
        m = ''.join(time_date.split(','))
        b = m.split(' ')
        if 'ago' in b:
            if 'days' in b:
                pattern = re.compile(u'(\d+)')
                data = int(re.findall(pattern, m)[0])
                time1 = time.localtime(time.time() - 86400 * data)
                timeclean = time.mktime(time1)
                # print  timeclean

            if 'day' in b:
                pattern = re.compile(u'(\d+)')
                data = int(re.findall(pattern, m)[0])
                time1 = time.localtime(time.time() - 86400 * data)
                timeclean = time.mktime(time1)
                # print  timeclean

            elif 'hours' in b:
                pattern = re.compile(u'(\d+)')
                data = int(re.findall(pattern, m)[0])
                time1 = time.localtime(time.time() - 3600 * data)
                timeclean = time.mktime(time1)
                # print  timeclean
            elif 'minutes' in b:
                pattern = re.compile(u'(\d+)')
                data = int(re.findall(pattern, m)[0])
                time1 = time.localtime(time.time() - 60 * data)
                timeclean = time.mktime(time1)
                # print  timeclean

            else:
                print('ok')
        else:
            timeclean = time.mktime(time.strptime(m.strip(' '), "%b %d %Y"))
        return timeclean

    def req_url(self, query, language=None, start=0, pause=2):
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

        # time.sleep(pause)
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
            LOGGER.info(url)
            time.sleep(pause)
            content = r.content
            charset = cchardet.detect(content)
            bsObj = content.decode(charset['encoding'])
            return bsObj
        except (ValueError, Exception) as e:
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

    def pq_html(self, content):
        return pq(content)

    def get_random_user_agent(self):
        return random.choice(self.get_data('user_agents.txt', USER_AGENT))

    def get_random_domain(self):
        domain = random.choice(self.get_data('all_domain.txt', DOMAIN))
        if domain in BLACK_DOMAIN:
            self.get_random_domain()
        else:
            return domain

    def get_data(self, filename, default=''):
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


news = MagicGoogle_News()
data = news.gain_data('债券 预期收益')
