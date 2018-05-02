# -*- coding: utf-8 -*-
"""
Created on Mon Jan 29 19:02:07 2018

@author: Miniroses
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
import cchardet
import random
import sys
import time
import cchardet
import requests
# import demjson
headers = {
'Content-Type':'application/json;charset=UTF-8',
'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.36'
             }
proxies = { "http": "http://127.0.0.1:1080", "https": "http://127.0.0.1:1080"}
url='https://scholar.google.com/scholar?lr=&q=lda+finance&hl=zh-CN'
Resp2=requests.get(url,headers=headers,proxies=proxies)
print Resp2
html = Resp2.text
bsObj = BeautifulSoup(html, "lxml")



breif_counts=bsObj.find_all('div',id='gs_ab_md')[0].text
print breif_counts

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
        else:
            Author=items[0]
            print Author
            public=items[1]
            print public
            source=None

    if iid.find('div',class_='gs_rs') is not None:
        abstarct= iid.find('div',class_='gs_rs').text
        print abstarct
    if len(iid.find_all('div',class_='gs_ggsd'))!=0:
        download_link= iid.find_all('div',class_='gs_ggsd')[0].text
        print download_link
    if iid.find_all('div',class_='gs_fl') is not None:
        if len(iid.find_all('div',class_='gs_fl'))==2:
            cited= iid.find_all('div',class_='gs_fl')[1].text
            pattern=re.compile(u'被引用次数：(\d+) 相关文章')
            cited_counts=int(re.findall(pattern,cited)[0])
            print cited_counts
        elif len(iid.find_all('div',class_='gs_fl'))==1:
            cited=iid.find_all('div',class_='gs_fl')[0].text
            pattern=re.compile(u'被引用次数：(\d+) 相关文章')
            cited_counts=int(re.findall(pattern,cited)[0])
            print cited_counts
        else:
            pass
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



    print '*'*100
