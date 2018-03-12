import os
import random
import sys
import time
import re
import cchardet
import requests

from pyquery import PyQuery as pq
from MagicGoogle.config import USER_AGENT, DOMAIN, BLACK_DOMAIN, URL_SEARCH,  LOGGER

if sys.version_info[0] > 2:
    from urllib.parse import quote_plus, urlparse, parse_qs
else:
    from urllib import quote_plus
    from urlparse import urlparse, parse_qs


class MagicGoogle():
    """
    Magic google search.
    """
    
    def __init__(self, rate_delay=2, error_delay=5):

        PROXIES = [{
            'http': 'http://127.0.0.1:1080' ,
            'https': 'http://127.0.0.1:1080'
        }]

        self.rate_delay = rate_delay
        self.error_delay = error_delay
        self.proxies = random.choice(PROXIES)

        
        
    def counts_result(self,bsObj): 
        
        pq_content = self.pq_html(bsObj)
        m=pq_content('div.sd')[0].text
        if start==0:
            pattern = re.compile(u'(\d+)')
            result_count = int(''.join(re.findall(pattern,m)))
            return result_count
        else:
            pattern = re.compile(u'(\d+)')
            result_count = int(''.join(re.findall(pattern,m)[1:]))
            return result_count




    def content(self, bsObj ):       
        pq_content = self.pq_html(bsObj)
        result = []
        for item in pq_content('div.g').items():
            information = {
                'title':None,
                'url':None,
                'text':None
                }
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


    def gain_data(self, query, language=None,  start=0, nums=100,pause=2):
        start=0
        init_url=self.req_url(query, start,language, pause=2)
        bsObj=self.Cold_boot(url)
        total_count=self.counts_result(bsObj)
        pages=int(ceil(nums/20))
        page=0
        all_info=[]
        while page<pages:
            print page
            start=page*20
            url=self.req_url(query, start,language, pause=2)
            print url
            bsObj=self.Cold_boot(url)
            info=self.content(bsObj)
            all_info=all_info+info
            page=page+1
        infos={
        'total_count':total_count,
        'url':init_url,
        'all_info':all_info
        }           
        return infos
    
            
    def search_relation(self, bsObj, pause=2):

        relation_kw=[]
        pq_content = self.pq_html(bsObj)
        for item in pq_content('p._Bmc').items():
            href = item('a').attr('href')
            if href:
                o = urlparse(href, 'http')
                if o.netloc:
                    kw=href
                if href.startswith('/search?'):
                    href = parse_qs(o.query)['q'][0]
                    o = urlparse(href, 'http')
                    if o.path:
                        kw=href                        
                relation_kw.append(kw)
        return relation_kw
            
    def req_url(self, query, language=None,  start=0, pause=2):
        time.sleep(pause)
        
        url = URL_SEARCH
        url = url.format(query=quote_plus(query),language=language,start=start)
        if language is None:
            url = url.replace('hl=None&', '')
        return url

    def Cold_boot(self, url, pause=2):
        time.sleep(pause)
        domain = self.get_random_domain()
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
            bsObj = content.decode(charset['encoding'])
            return bsObj
        except (ValueError,Exception) as e:
            print e.message
            print "Sleeping for %i" % self.error_delay
            sleep(self.error_delay)
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
        root_folder = os.path.dirname(__file__)
        user_agents_file = os.path.join(
            os.path.join(root_folder, 'data'), filename)
        try:
            with open(user_agents_file) as fp:
                data = [_.strip() for _ in fp.readlines()]
        except:
            data = [default]
        return data

    

    


        


        

