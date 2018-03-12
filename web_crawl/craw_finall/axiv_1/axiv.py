# -*- coding: utf-8 -*-
"""
Created on Tue Jan 23 15:41:17 2018

@author: zhaohua
"""


import sys
# import urllib2
import time
from bs4 import BeautifulSoup
from selenium import webdriver
# reload(sys)
# sys.setdefaultencoding('utf8') # 设置编码
import re
import time
from bs4 import BeautifulSoup
from selenium import webdriver




class seleniumTest():
    def __init__(self):
        self.driver = webdriver.PhantomJS(executable_path=r'phantomjs.exe')
       
    def Cold_boot(self,url):
    # 初始网页启动
        try:
            time.sleep(0.02)
            Resp2=requests.get(url) 
            content = Resp2.content
            charset = cchardet.detect(content)
            html = content.decode(charset['encoding'])
            bsObj = BeautifulSoup(html, "lxml")
        except :
            return None
        return bsObj

    def web_boot(self,driver, page):
        if page==0:
            click_page = '//*[@id="dlpage"]/a[4]'
            driver.find_element_by_xpath(click_page).click()
            time.sleep(0.06)
            try:
                bsObj = BeautifulSoup(driver.page_source, "lxml")
            except AttributeError as e:
                return None
            return driver, bsObj
        else:
            click_page = '//*[@id="dlpage"]/a[6]'
            driver.find_element_by_xpath(click_page).click()
            time.sleep(0.06)
            try:
                bsObj = BeautifulSoup(driver.page_source, "lxml")
            except AttributeError as e:
                return None
            return driver, bsObj

    def gain_data(self,keyword,pages):
        url=self.construct_url(keyword)
        all_info=[]
        driver = self.driver
        driver.get(url) 
        bsObj=self.Cold_boot(url)
        total_count,curr_total=self.Total_counts(bsObj)
        page=0
        base_url='https://arxiv.org{}'
        while page<pages:
            print page
            if page==0: 
                if total_count<25:
                    for iid in bsObj.find_all('span',class_='list-identifier'):   
                        url1= iid.find('a').attrs['href']
                        url=base_url.format(url1)
                        print url
                        info=self.content(url)
                        all_info=all_info+info
                    break
                else:
                    for iid in bsObj.find_all('span',class_='list-identifier'):   
                        url1= iid.find('a').attrs['href']
                        url=base_url.format(url1)
                        print url
                        info=self.content(url)
                        all_info=all_info+info
                    driver, bsObj=self.web_boot(driver,page)                
            else:
                bsObj = BeautifulSoup(driver.page_source, 'xml')
                total_count,curr_total=self.Total_counts(bsObj)
                if total_count-curr_total+1<=25:
                    for iid in bsObj.find_all('span',class_='list-identifier'):   
                        url1= iid.find('a').attrs['href']
                        url=base_url.format(url1)
                        print url
                        info=self.content(url)
                        all_info=all_info+info
                    break
                else:
                    for iid in bsObj.find_all('span',class_='list-identifier'):   
                        url1= iid.find('a').attrs['href']
                        url=base_url.format(url1)
                        print url
                        info=self.content(url)
                        all_info=all_info+info               
                    driver, bsObj=self.web_boot(driver,page)
            page=page+1
        return all_info
        
    def Total_counts(self,bsObj):
        if len(bsObj.find_all('h3'))>1:           
            m=bsObj.find_all('h3')[1].text
            pattern=re.compile('of (\d+) total')
            total_count = int(re.findall(pattern,m)[0])
            print total_count
            pattern2=re.compile('results (\d+) through')
            current_count = int(re.findall(pattern2,m)[0])
            print current_count
        else:
            m=bsObj.find_all('h3')[0].text
            print m
            pattern=re.compile('of (\d+) total')
            print re.findall(pattern,m)
            total_count = int(re.findall(pattern,m)[0])
            print total_count
            pattern2=re.compile('results (\d+) through')
            current_count = int(re.findall(pattern2,m)[0])
            print current_count
        return total_count,current_count
                
    def content(self,url):
        #####最底层内容###
        bsObj=self.Cold_boot(url)
        data=[]           
        for iid in bsObj.find_all('div',class_='leftcolumn'):
            Statistics=iid.find_all('div',class_='subheader')[0].text.replace('\n', '').replace('\t', '').strip(' ')         
            Title=iid.find_all('h1',class_={'title','mathjax'})[0].text.replace('\n', '').replace('\t', '').strip(' ')
            Authors=iid.find_all('div',class_='authors')[0].text.replace('\n', '').replace('\t', '').strip(' ')
            dateline=iid.find_all('div',class_='dateline')[0].text.replace('\n', '').replace('\t', '').strip(' ')   
            Abstract=iid.find_all('blockquote',class_={'abstract','mathjax'})[0].text.replace('\n', '').replace('\t', '').strip(' ')       
            Comments=iid.find_all('td',class_={'tablecell','comments'})[1].text.replace('\n', '').replace('\t', '').strip(' ')       
            print dateline
            information={
                    'Statistics':Statistics,
                    'Title':Title,
                    'Authors':Authors,
                    'dateline':dateline,
                    'Abstract':Abstract,
                    'Comments':Comments,
                    'url':url
        
              }
              
            data.append(information) 
        return data
            
    def construct_url(self,keyword):
        global url
        m=keyword.split(' ')
        
        print m
        if len(m)==1:
            base_url='https://arxiv.org/find/all/1/all:+{}/0/1/0/all/0/1'
            url=base_url.format(keyword)
        elif len(m)==2:
            base_url='https://arxiv.org/find/all/1/all:+AND+{}+{}/0/1/0/all/0/1'
            url=base_url.format(m[0],m[1])
        elif len(m)==3:
            base_url='https://arxiv.org/find/all/1/all:+AND+{}+AND+{}+{}/0/1/0/all/0/1'
            url=base_url.format(m[2],m[0],m[1])
        elif len(m)==3:
            base_url='https://arxiv.org/find/all/1/all:+AND+{}+AND+{}+AND+{}+{}/0/1/0/all/0/1'
            url=base_url.format(m[3],m[2],m[0],m[1])
        else:
            pass
        return url
#    def get_dict(self,keyword):
#        all_info={}
#        counts=self.Total_counts()
#        url=self.construct_url(keyword)
#        info=self.gain_data()
#        all_info['counts']=counts
#        all_info['url']=url
#        all_info['info']=info
#        return all_info

        
        
        
        
        
        
        
            
            
        
        
mg=seleniumTest()
#keyword='bayesian network finance'
keyword='svm finance'
pages=5
data_all=mg.gain_data(keyword,pages)



