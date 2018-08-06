# -*- coding: utf-8 -*-
"""
Created on Wed Jan 31 10:55:23 2018

@author: Minirose
"""

import re
import pandas as pd
import os 
import bs4
from bs4 import BeautifulSoup
import time
import pandas as pd
from pandas import DataFrame
import cchardet
import random
import sys
import time
import cchardet
import requests
import demjson
url='http://zhihu.sogou.com/zhihu?query=finance&ie=utf8&dp=1&w=&sut=11265&sst0=1517367236918&lkt=5%2C1517367232192%2C1517367236815'
#url='http://weixin.sogou.com/weixin?query=fiance&_sug_type_=&s_from=input&_sug_=n&type=2&page=2&ie=utf8&w=01019900'
#url='http://weixin.sogou.com/weixin?type=2&s_from=input&query=fiance+2017&ie=utf8&_sug_=n&_sug_type_=&w=01019900
headers = {
'Content-Type':'application/json;charset=UTF-8',
'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.36'
             }
proxies = { "http": "http://127.0.0.1:1080", "https": "http://127.0.0.1:1080"}

Resp2=requests.get(url,headers=headers,proxies=proxies) 

print Resp2
html = Resp2.text
bsObj = BeautifulSoup(html, "lxml")

#breif_counts= bsObj.find_all('div',class_='mun')[0].text
#pattern=re.compile(u'(\d+)')
#result_counts= int(re.findall(pattern,breif_counts)[0])


for item in bsObj.find_all('div',class_='box-result'):
#    print item
    for iid in item.find_all('div',class_='result-about-list'):
        user_1=None
        user_2=None
#        print iid.find_all('h4',class_='about-list-title')[0]
   
        contents= iid.find_all('h4',class_='about-list-title')[0]
        Link= contents.find('a').attrs['href']
#        print Link
        Title= contents.find('a').text
#        print Title
        Abstract=iid.find_all('p',class_='about-answer')[0]
#        print Abstract
        favorate_txt= Abstract.find_all('span',class_='count')[0].text
        pattern=re.compile(u'(\d+)')
        favorate_counts= int(re.findall(pattern,favorate_txt)[0])
#        print favorate_counts
#        print Abstract.find_all('a')
        if len(Abstract.find_all('cite'))!=0:
            user_1= Abstract.find_all('cite')[0].text
            print user_1
        if len(Abstract.find_all('a'))!=0:
            user_2= Abstract.find_all('a')[0].text
            print user_2
        
        Anwser_content= iid.find_all('span',class_='answer-num')[0]
        anwser_link= Anwser_content.find('a').attrs['href']
        print anwser_link
        anwser_txt=Anwser_content.find('a').text
        pattern=re.compile(u'(\d+)')
        anwser_counts= int(re.findall(pattern,anwser_txt)[0])
        print anwser_counts
        
        infos={
        'Link':Link,
        'Title':Title,
        'Abstract':Abstract,
        'favorate_counts':favorate_counts,
        'user_1':user_1,
        'anwser_link':anwser_link,
        'anwser_counts':anwser_counts,
        'user_2':user_2

           }
        
        
        print '*'*50
        
        
import weixinsogou
from weixinsogou import weixinsogou
PROXIES = [{
            'http': 'http://127.0.0.1:1080',
            'https': 'http://127.0.0.1:1080'
        }]
mg=weixinsogou.Weixinsogou(PROXIES)
query='fiance 2017'
infos=mg.gain_data(query,nums=220)
