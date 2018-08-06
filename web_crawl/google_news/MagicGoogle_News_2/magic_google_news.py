import os
import random
import sys
import time
import re
import cchardet
import requests

from pyquery import PyQuery as pq
from MagicGoogle_News.config import USER_AGENT, DOMAIN, BLACK_DOMAIN, URL_SEARCH, URL_NEXT, URL_NUM, LOGGER

if sys.version_info[0] > 2:
    from urllib.parse import quote_plus, urlparse, parse_qs
else:
    from urllib import quote_plus
    from urlparse import urlparse, parse_qs


class MagicGoogle_News():
    """
    Magic google search.
    """
    
    def __init__(self, proxies=None):
        self.proxies = random.choice(proxies) 
        if proxies :pass
        else :None
        
        
    def counts_result(self, keywords, language=None, num=None, start=0, pause=2):

        content = self.search_page(keywords, language, num, start, pause)
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


    def search_news(self, keywords, language=None, num=None, start=0, pause=2):
       
        """
        Get the results you want,such as title,description,url
        :param query:
        :param language:
        :param num:
        :param start:
        :return: Generator
        """
        
        content = self.search_page(keywords, language, num, start, pause)
        pq_content = self.pq_html(content)
        result_new = []
        for item in pq_content('div.g').items():
            href = item('h3.r>a').eq(0).attr('href')   
            title= item('h3.r>a').eq(0).text()
            print title
            if href:
                url = self.filter_link(href)
                print url
            
            text1 = item('div.st')[0].text
            print text1
            source=item('span.f')[0].text.split('-')
            if len(source)>2:
                main_source=''.join(source[:-1])
                print main_source
                a=source[-1]
                tt=self.clear_time(a)
                print tt

            else:
                main_source=''.join(source[0])
                print main_source
                a=source[-1]
                tt=self.clear_time(a)
                print tt

            information = {
                        'title':title,
                        'url':url,
                        'text':text1,
                        'source':main_source,
                        'time':tt
                        }
                
            result_new.append(information)
        return result_new 

    def clear_time(self, time_date):
        import time
        global timeclean
        m=''.join(time_date.split(','))
        b=m.split(' ')
        if 'ago' in b:
            if 'days' in b:
                pattern = re.compile(u'(\d+)')
                data=int(re.findall(pattern,m)[0])
                time1=time.localtime(time.time()-86400*data)
                timeclean=time.mktime(time1)   
            elif 'hours' in b:
                pattern = re.compile(u'(\d+)')
                data=int(re.findall(pattern,m)[0])
                time1=time.localtime(time.time()-3600*data)
                timeclean=time.mktime(time1)
            elif 'minutes' in b:
                pattern = re.compile(u'(\d+)')
                data=int(re.findall(pattern,m)[0])
                time1=time.localtime(time.time()-60*data)
                timeclean=time.mktime(time1)
            else:
                print 'ok'
        else:
            timeclean=time.mktime(time.strptime(m.strip(' '),"%b %d %Y"))
        return timeclean
            
    def req_url(self, keywords, language=None, num=None, start=0, pause=2):
        time.sleep(pause)
        query=self.get_query(keywords)
        domain = self.get_random_domain()
        if start > 0:
            url = URL_NEXT
            url = url.format(
                domain=domain, language=language, query=query, num=num, start=start)
        else:
            if num is None:
                url = URL_SEARCH
                url = url.format(
                    domain=domain, language=language, query=query)
            else:
                url = URL_NUM
                url = url.format(
                    domain=domain, language=language, query=query, num=num)
        if language is None:
            url = url.replace('hl=None&', '')
        return url

    def search_page(self, keywords, language=None, num=None, start=0, pause=2):
        
        """
        Google search
        :param query: Keyword
        :param language: Language
        :return: result
        """
        time.sleep(pause)
        query=self.get_query(keywords)
        domain = self.get_random_domain()
        if start > 0:
            url = URL_NEXT
            url = url.format(
                domain=domain, language=language, query=query, num=num, start=start)
        else:
            if num is None:
                url = URL_SEARCH
                url = url.format(
                    domain=domain, language=language, query=query)
            else:
                url = URL_NUM
                url = url.format(
                    domain=domain, language=language, query=query, num=num)
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

    def search_url(self, keywords, language=None, num=None, start=0, pause=2):
       
        """
        :param query:
        :param language:
        :param num:
        :param start:
        :return: Generator
        """
        content = self.search_page(keywords, language, num, start, pause)
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



    def all_data(self, keywords, language=None, num=None, start=0, pause=2):
        """
        Get data from a file
        :param filename: filename
        :param default: default value
        :return: data
        """
        finall_data={}
        finall_data['req_url']=self.req_url(keywords, language, num, start, pause)
        finall_data['result_count']=self.counts_result(keywords, language, num, start, pause)
        finall_data['top_result']=self.search_news(keywords, language, num, start, pause)
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

    def get_query(self,keywords):
        clean_query=re.sub(' ','+',keywords)
        return clean_query

     


        

