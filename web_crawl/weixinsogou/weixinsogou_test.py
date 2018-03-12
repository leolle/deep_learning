# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 16:29:02 2018

@author: Administrator
"""
import requests
import re
import pandas as pd
import os 
import bs4
from bs4 import BeautifulSoup
import time
import pandas as pd
from pandas import DataFrame
import os
import cchardet
import os
import random
import sys
import time
import cchardet
import requests
import demjson
url='http://weixin.sogou.com/weixin?query=fiance&_sug_type_=s_from=input&_sug_=n&type=2&page=3&ie=utf8&w=01019900'
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
breif_counts= bsObj.find_all('div',class_='mun')[0].text
pattern=re.compile(u'(\d+)')
result_counts= int(re.findall(pattern,breif_counts)[0])
for item in bsObj.find_all('ul',class_='news-list'):
    for iid in item.find_all('li'):
        contents= iid.find_all('div',class_='txt-box')[0]
        Link= contents.find('a').attrs['href']
        Title= contents.find('a').text
        Abstract=iid.find_all('p',class_='txt-info')[0].text
        author_time=iid.find_all('a',class_='account')[0]
        source_link= author_time.attrs['href']
        Source=author_time.text
        timeConvert=iid.find('span','s2').text
        pattern=re.compile(u'(\d+)')
        Time= int(re.findall(pattern,timeConvert)[0])
        
        infos={
        'Link':Link,
        'Title':Title,
        'Abstract':Abstract,
        'source_link':source_link,
        'Source':Source,
        'Time':Time
           }
        
        
        print '*'*50
