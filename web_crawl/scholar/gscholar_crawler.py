"""
# XXX: selenium.common.exceptions.WebDriverException: Message: 'chromedriver' executable may have wrong permissions. Please see https://sites.google.com/a/chromium.org/chromedriver/home
"""
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import os
import numpy as np
from getproxy import getproxy
import hashlib
from selenium.common.exceptions import TimeoutException
import time

import pandas as pd

page_count = 0
max_page_count = 100

PROXY = '192.168.126'
DEBUG = 0
useProxy = 0


def scrapeLandingPage():
    global page_count, PROXY, proxyDF
    page_count = 0
    if (DEBUG):
        print("In Landing Page")

    if (useProxy):
        proxyObj = getproxy()
        proxyDF = proxyObj.getProxy()
        PROXY = proxyDF.loc[page_count, 'ip'] + ":" + proxyDF.loc[page_count,
                                                                  'port']
        if (DEBUG): print('using PROXY ', PROXY)

    scholarProfiles = open(
        'scholarProfile' + str(int(time.time())) + '.csv', mode='w')

    # Starting node link
    #url = 'https://scholar.google.com/citations?view_op=search_authors&hl=en&mauthors=label:machine_learning'
    #url = 'https://scholar.google.com/citations?view_op=view_org&org=17554517495610703090&hl=en&oi=io'
    url = 'https://scholar.google.com/citations?view_op=view_org&org=21288157106126462&hl=en&oi=io'
    url = 'https://scholar.google.com/citations?view_op=view_org&org=14823011757688503605&hl=en&oi=io'
    url = 'https://scholar.google.com/citations?view_op=view_org&hl=en&org=6037664147916511730'
    url = 'https://scholar.google.com/citations?view_op=view_org&hl=en&org=8867661471528740601'
    url = 'https://scholar.google.com/citations?view_op=view_org&hl=en&org=13546425071114014240'
    url_about = url

    depth = 0
    max_depth = 50
    button = 1
    chromedriver = "chromedriver"  # Needed?
    os.environ["webdriver.chrome.driver"] = chromedriver  # Needed?
    options = webdriver.ChromeOptions()
    while 1:
        try:
            #options.add_argument('--headless')
            #options.add_argument('--disable-gpu')
            if (useProxy):
                options.add_argument('--proxy-server=http://%s' % PROXY)

            browser = webdriver.Chrome(chrome_options=options)
            browser.set_page_load_timeout(30)
            browser.get(url_about)
            break
        except TimeoutException:
            browser.quit()
            page_count += 1
            if (useProxy):
                PROXY = proxyDF.loc[page_count,
                                    'ip'] + ":" + proxyDF.loc[page_count, 'port']
                print('using PROXY ', PROXY)
            continue

        topic = url_about[81:]
        if (DEBUG): print(topic)

    time.sleep(np.random.randint(3))
    #die on timeout
    while depth < max_depth:

        depth += 1
        #grab a new proxy if the page count has exceeded
        #test this!!
        if depth > max_depth and useProxy == 1:
            #reset page-count
            depth = 0
            proxyObj = getproxy()
            proxyDF = proxyObj.getProxy()
            PROXY = proxyDF.loc[page_count,
                                'ip'] + ":" + proxyDF.loc[page_count, 'port']
            print('using PROXY ', PROXY)

        if depth > 1:
            try:
                if DEBUG: print("clicked the next button")
                button.click()
            except TimeoutException:
                if DEBUG: print('exception block')
                browser.quit()
                page_count += 1
                if useProxy:
                    PROXY = proxyDF.loc[page_count,
                                        'ip'] + ":" + proxyDF.loc[page_count,
                                                                  'port']
                    if DEBUG: print('using PROXY ', PROXY)
                    options.add_argument('--proxy-server=http://%s' % PROXY)
                #options.add_argument('--headless')
                #options.add_argument('--disable-gpu')

                browser = webdriver.Chrome(chrome_options=options)
                browser.set_page_load_timeout(30)
                button.click()
        if DEBUG: print('out of shit')
        try:
            time.sleep(np.random.randint(3))
            if DEBUG: print("extracting info")
            profileBlocks = browser.find_elements_by_xpath(
                '//*[@id="gsc_sa_ccl"]/*')
            for profileContentsXpath in profileBlocks:
                if DEBUG: print('+++++++++++++++++++++++++++++++++++++')
                try:
                    user_url = profileContentsXpath.find_element_by_xpath(
                        "./div/h3/a").get_attribute('href')
                    user_name = profileContentsXpath.find_element_by_xpath(
                        "./div/h3/a").text
                    affiliation = profileContentsXpath.find_element_by_xpath(
                        "./div/div[1]").text
                    verification_id = profileContentsXpath.find_element_by_xpath(
                        "./div/div[2]").text
                    citation_text = profileContentsXpath.find_element_by_xpath(
                        "./div/div[3]").text
                    tag_text = profileContentsXpath.find_element_by_xpath(
                        "./div/div[4]").text
                    if DEBUG:
                        print(user_name, user_url, affiliation, verification_id,
                              citation_text, tag_text)
                    scholarProfiles.write((user_name + '####' + user_url + '####' + affiliation + '####' \
                            + verification_id + '####' + citation_text + '####' +tag_text + '\n').encode('utf8'))
                except:
                    continue

            browser.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")
            button = browser.find_element_by_xpath(
                '//*[@id="gsc_authors_bottom_pag"]/div/button[2]')
        except:
            break

    browser.quit()
    # File cleanup
    scholarProfiles.close()
    return


def main():
    scrapeLandingPage()
    return 0


if __name__ == "__main__":
    main()
main()
