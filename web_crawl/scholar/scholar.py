import os
import random
import sys
import time
import re
import cchardet
import requests
import pandas as pd
import bs4
from bs4 import BeautifulSoup
from pandas import DataFrame
from math import ceil
import config

from config import USER_AGENT,  URL_SEARCH, URL_NEXT, LOGGER

if sys.version_info[0] > 2:
    from urllib.parse import quote_plus, urlparse, parse_qs
else:
    from urllib import quote_plus
    from urlparse import urlparse, parse_qs


class Scholar():
    """
    scholar google search.
    """
    
    def __init__(self, proxies=None):
        self.proxies = random.choice(proxies) 
        if proxies :pass
        else :None
        
        
    def counts_result(self, bsObj):      
        breif_counts=bsObj.find_all('div',id='gs_ab_md')[0].text
        print breif_counts
        text1 = breif_counts.replace(r',', "")
#        print text1
        pattern=re.compile(u'\d+')
        result_count=re.findall(pattern,text1)[0]
        print result_count

        return result_count



    def content(self, bsObj,pause=2):
        global download_link
        global abstarct
        infomation=[]
        for iid in bsObj.find_all('div',class_={'gs_r' ,'gs_or' ,'gs_scl'}):
            Link= iid.find('a').attrs['href']
            print Link
            Title=iid.find('h3',class_='gs_rt').text
            print Title
            
            if len(iid.find_all('div',class_='gs_a'))!=0:       
                infos=iid.find_all('div',class_='gs_a')[0].text
                items=infos.split('-')
                if len(items)>2:
                    Author=items[0]
                    print Author
                    public=items[1]
                    print public
                    source='-'.join(items[2:])
                    print source
                elif len(items)==2:
                    print items
                    Author=items[0]
                    print Author
                    public=items[1]
                    print public
                    source=None
                else:
                    public=items[0]
                    print public
#                    print '*'*30
                
            if iid.find('div',class_='gs_rs') is not None:
                abstarct= iid.find('div',class_='gs_rs').text
                print abstarct
            if len(iid.find_all('div',class_='gs_ggsd'))!=0:       
                download_link= iid.find_all('div',class_='gs_ggsd')[0].text
                print download_link
            if iid.find_all('div',class_='gs_fl') is not None: 
                if len(iid.find_all('div',class_='gs_fl'))==2:
                    cited=iid.find_all('div',class_='gs_fl')[1].text.strip(' ').split(' ')
                    pattern=re.compile(u'(\d+)')
                    if len(re.findall(pattern,cited[0]))!=0:
                        cited_counts=int(re.findall(pattern,cited[0])[0])
                        print cited_counts
                    else:
                        cited_counts=0
                        
                elif len(iid.find_all('div',class_='gs_fl'))==1:
                    cited=iid.find_all('div',class_='gs_fl')[0].text.strip(' ').split(' ')
                    pattern=re.compile(u'(\d+)')
                    if len(re.findall(pattern,cited[0]))!=0:                        
                        cited_counts=int(re.findall(pattern,cited[0])[0])
                        print cited_counts
                    else:
                        cited_counts=0
                        
                else:
                    cited_counts=0
            infos={
                'Link':Link,
                'Title':Title,
                'Author':Author,
                'public':public,
                'source':source,
                'abstarct':abstarct,
                'download_link':download_link,
                'cited_counts':cited_counts
                   }
            infomation.append(infos)
    
        return infomation 

    
    def req_url(self, query, start, pause=2):
        time.sleep(pause)
#        domain = ''
        if start > 0:
            url = URL_NEXT
            url = url.format(query=quote_plus(query),start=start)
        else:
            
            url = URL_SEARCH
            url = url.format(query=quote_plus(query))
        return url

    def Cold_boot(self, url, pause=2):
        
        time.sleep(pause)
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
            bsObj = BeautifulSoup(text, "lxml")
            return bsObj
        except Exception as e:
            LOGGER.exception(e)
            return None

    

    def get_random_user_agent(self):
        """
        Get a random user agent string.
        :return: Random user agent string.
        """
        return random.choice(self.get_data('user_agents.txt', USER_AGENT))




    def gain_data(self, query, nums=None,pause=2):
        start=0
        url=self.req_url(query, start, pause=2)
        bsObj=self.Cold_boot(url)
        total_count=self.counts_result(bsObj)
        pages=int(ceil(nums/10))
        page=0
        all_info=[]
        while page<pages:
            print page
            start=page*10
            url=self.req_url(query, start, pause=2)
            print url
            bsObj=self.Cold_boot(url)
            info=self.content(bsObj,pause=2)
            all_info=all_info+info
            page=page+1
        infos={
        'total_count':total_count,
        'url':url,
        'all_info':all_info
        }

                    
        return infos

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

     


        

