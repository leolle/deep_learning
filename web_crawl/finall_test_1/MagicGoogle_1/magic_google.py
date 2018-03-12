import os
import random
import sys
import time
import re
import cchardet
import requests

from pyquery import PyQuery as pq
from MagicGoogle.config import USER_AGENT, DOMAIN, BLACK_DOMAIN, URL_SEARCH, URL_NEXT, URL_NUM, LOGGER

if sys.version_info[0] > 2:
    from urllib.parse import quote_plus, urlparse, parse_qs
else:
    from urllib import quote_plus
    from urlparse import urlparse, parse_qs


class MagicGoogle():
    """
    Magic google search.
    """
    
    def __init__(self, proxies=None):
        self.proxies = random.choice(proxies) 
        if proxies :pass
        else :None
        
        
    def counts_result(self, query, language=None, num=None, start=0, pause=2):      
        content = self.search_page(query, language, num, start, pause)
        pq_content = self.pq_html(content)
        m=pq_content('div.sd')[0].text
        if start==0:
            pattern = re.compile(u'(\d+)')
            result_count = int(''.join(re.findall(pattern,m)))
            return result_count
        else:
            pattern = re.compile(u'(\d+)')
            result_count = int(''.join(re.findall(pattern,m)[1:]))
            return result_count




    def search(self, query, language=None, num=None, start=0, pause=2):
       
        """
        Get the results you want,such as title,description,url
        :param query:
        :param language:
        :param num:
        :param start:
        :return: Generator
        """

        content = self.search_page(query, language, num, start, pause)
        pq_content = self.pq_html(content)
        result = []
        for item in pq_content('div.g').items():
            title= item('h3.r>a').eq(0).text()
            href = item('h3.r>a').eq(0).attr('href')
            if href:
                url = self.filter_link(href)
            text = item('span.st').text()
            information = {
                'title':title,
                'url':url,
                'text':text
                }
            result.append(information)
        return result
            
    def search_relation(self, query, language=None, num=None, start=0, pause=2):
        
        """
        Get the relation results you want,such as title,url
        :param query:
        :param language:
        :param num:
        :param start:
        :return: Generator
        """
        relation_kw=[]
        content = self.search_page(query, language, num, start, pause)
        pq_content = self.pq_html(content)
        for item in pq_content('p._Bmc').items():
            href = item('a').attr('href')
            if href:
                o = urlparse(href, 'http')
                if o.netloc: 
                if href.startswith('/search?'):
                    href = parse_qs(o.query)['q'][0]
                    o = urlparse(href, 'http')
                    if o.path:
                relation_kw.append(href)
        return relation_kw
            
    def req_url(self, query, language=None, num=None, start=0, pause=2):
        time.sleep(pause)
        domain = self.get_random_domain()
        if start > 0:
            url = URL_NEXT
            url = url.format(
                domain=domain, language=language, query=quote_plus(query), num=num, start=start)
        else:
            if num is None:
                url = URL_SEARCH
                url = url.format(
                    domain=domain, language=language, query=quote_plus(query))
            else:
                url = URL_NUM
                url = url.format(
                    domain=domain, language=language, query=quote_plus(query), num=num)
        if language is None:
            url = url.replace('hl=None&', '')
        return url

    def search_page(self, query, language=None, num=None, start=0, pause=2):
        
        """
        Google search
        :param query: Keyword
        :param language: Language
        :return: result
        """
        time.sleep(pause)
        domain = self.get_random_domain()
        if start > 0:
            url = URL_NEXT
            url = url.format(
                domain=domain, language=language, query=quote_plus(query), num=num, start=start)
        else:
            if num is None:
                url = URL_SEARCH
                url = url.format(
                    domain=domain, language=language, query=quote_plus(query))
            else:
                url = URL_NUM
                url = url.format(
                    domain=domain, language=language, query=quote_plus(query), num=num)
        if language is None:
            url = url.replace('hl=None&', '')
        headers = {'user-agent': self.get_random_user_agent()}
        try:
            requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
            r = requests.get(url=url,
                             proxies=self.proxies,
                             headers=headers,
                             allow_redirects=False,
                             verify=False,
                             timeout=30)
            LOGGER.info(url)
            content = r.content
            charset = cchardet.detect(content)
            text = content.decode(charset['encoding'])
            return text
        except Exception as e:
            LOGGER.exception(e)
            return None

    def search_url(self, query, language=None, num=None, start=0, pause=2):
       
        """
        :param query:
        :param language:
        :param num:
        :param start:
        :return: Generator
        """
        content = self.search_page(query, language, num, start, pause)
        pq_content = self.pq_html(content)
        for item in pq_content('h3.r').items():
            href = item('a').attr('href')
            if href:
                url = self.filter_link(href)
                if url:
                    yield url

    def filter_link(self, link):
        """
        Returns None if the link doesn't yield a valid result.
        Token from https://github.com/MarioVilas/google
        :return: a valid result
        """
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
        """
        Parsing HTML by pyquery
        :param content: HTML content
        :return:
        """
        return pq(content)

    def get_random_user_agent(self):
        """
        Get a random user agent string.
        :return: Random user agent string.
        """
        return random.choice(self.get_data('user_agents.txt', USER_AGENT))

    def get_random_domain(self):
        """
        Get a random domain.
        :return: Random user agent string.
        """
        domain = random.choice(self.get_data('all_domain.txt', DOMAIN))
        if domain in BLACK_DOMAIN:
            self.get_random_domain()
        else:
            return domain



    def all_data(self, query, language=None, num=None, start=0, pause=2):
        """
        Get data from a file
        :param filename: filename
        :param default: default value
        :return: data
        """
        finall_data={}
        finall_data['req_url']=self.req_url(query, language, num, start, pause)
        finall_data['result_count']=self.counts_result(query, language, num, start, pause)
        finall_data['top_result']=self.search(query, language, num, start, pause)
        finall_data['relation_kw']=self.search_relation(query, language, num, start, pause)
        return finall_data

    def get_data(self, filename, default=''):
        """
        Get data from a file
        :param filename: filename
        :param default: default value
        :return: data
        """
        root_folder = os.path.dirname(__file__)
        user_agents_file = os.path.join(
            os.path.join(root_folder, 'data'), filename)
        try:
            with open(user_agents_file) as fp:
                data = [_.strip() for _ in fp.readlines()]
        except:
            data = [default]
        return data


    

    


        


        

