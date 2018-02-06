# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests
import csv
import bs4


#检查url地址
def check_link(url):
    try:

        r = requests.get(url)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except:
        print('无法链接服务器！！！')


#爬取资源
def get_contents(ulist, rurl):
    soup = BeautifulSoup(rurl, 'lxml')
    trs = soup.find_all('tr')
    for tr in trs:
        ui = []
        for td in tr:
            ui.append(td.string)
        ulist.append(ui)


#保存资源
def save_contents(urlist):
    with open("D:/2016年中国企业500强排行榜.csv", 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['2016年中国企业500强排行榜'])
        for i in range(len(urlist)):
            writer.writerow([urlist[i][0], urlist[i][1], urlist[i][2]])


urli = []
url = "http://web.stanford.edu/class/cs224n/syllabus.html"
rs = check_link(url)
get_contents(urli, rs)

#    save_contents(urli)
