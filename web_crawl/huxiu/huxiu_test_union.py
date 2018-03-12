# -*- coding: utf-8 -*-
"""
Created on Thu Jan 25 17:53:01 2018

@author: Administrator
"""

import unittest
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import re
import datetime

class seleniumTest(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.PhantomJS(executable_path=r'C:\Users\Administrator\Anaconda2\Lib\site-packages\selenium\webdriver\phantomjs\phantomjs.exe')

    def testEle(self):
        driver = self.driver
        driver.get('https://www.huxiu.com/search.html?s=%E8%82%A1%E7%A5%A8+%E5%9F%BA%E9%87%91+2017')
        soup = BeautifulSoup(driver.page_source, 'xml')
        while True:
            all_data=[]
            base_url='https://www.huxiu.com{}'
            tmn=int(soup.find_all('li',class_='active')[0].text)
            print tmn
        #        print bsObj.find_all('ul',class_='search-wrap-list-ul')
            for iid1 in soup.find_all('ul',class_='search-wrap-list-ul'):
                for iid in iid1.find_all('li'):
                    Title= iid.find('h2').text
                    link= iid.find('a').attrs['href']
                    Links=base_url.format(link) 
                    print Links
                    Content= iid.find('div',class_='mob-summay').text   
                    time_author= iid.find('div',class_='mob-author').text
                    pattern1=re.compile(u'(\D+)')        
                    author=re.findall(pattern1,time_author)[0]   
                    pattern2=re.compile(u'\d+-\d+-\d+ \d+:\d+')
                    time1=re.findall(pattern2,time_author)[0]
                    m=datetime.datetime.strptime(time1, "%Y-%m-%d %H:%M")         
                    Time=time.mktime(m.timetuple())                   
                    print Time
                    information={
                        'Title':Title,
                        'Links':Links,
                        'Content':Content,
                        'author':author,
                        'Time':Time
                  }

                all_data.append(information)
            if tmn<5:
                click_page = "/html/body/div[5]/div[1]/div[2]/nav/ul/li[%s]/a/i" %(tmn+6)
                driver.find_element_by_xpath(click_page).click()
                time.sleep(1)
            else:
                click_page = "/html/body/div[5]/div[1]/div[2]/nav/ul/li[10]/a/i" 
                driver.find_element_by_xpath(click_page).click()
                time.sleep(1)
            
            
            soup = BeautifulSoup(driver.page_source, 'xml')

    def tearDown(self):
        print 'down'

if __name__ == "__main__":
    unittest.main()