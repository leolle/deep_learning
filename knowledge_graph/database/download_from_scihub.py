# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import
from scihub2pdf import download as dl
import requests
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException

from PIL import Image
from scihub2pdf.tools import norm_url, download_pdf
from base64 import b64decode as b64d
from six import string_types
import sys
try:
    from StringIO import StringIO
    from io import BytesIO
except ImportError:
    from io import StringIO, BytesIO

try:
    s = requests.Session()
    driver = webdriver.PhantomJS(
        '/home/weiwu/Downloads/phantomjs-2.1.1-linux-x86_64/bin/phantomjs')
except WebDriverException:
    print("\n\t Install PhantomJS for download files in sci-hub.\n")
    print("\t OSX:")
    print("\t\t npm install -g phantomjs")
    print("\n\t Linux with npm:")
    print("\t\t sudo apt-get install npm\n")
    print("\t\t sudo npm install -g phantomjs\n")

doi = '10.1145/2449396.2449413'
pdf_file = """Directing Exploratory Search: Reinforcement Learning from
User Interactions with Keywords"""
domain_scihub = 'http://sci-hub.tw/'
sci_url = domain_scihub + doi
print("\n\tDOI: ", doi)
print("\tSci-Hub Link: ", sci_url)
r = requests.get(sci_url)
found = r.status_code == 200
if found:
    driver.get(sci_url)
    driver.set_window_size(1120, 550)
else:
    print("\tSomething is wrong with sci-hub,")
    print("\tstatus_code: ", r.status_code)
pdf = open(pdf_file, "wb")
pdf.write(r.content)
pdf.close()

dl.download_from_doi('10.1145/2449396.2449413')
url = 'https://dl.acm.org/citation.cfm?id=2387707'
# def download_from_scihub(doi, pdf_file):
#     found, r = ScrapSci.navigate_to(doi, pdf_file)
#     if not found:
#         return False, r

#     has_captcha, has_iframe = ScrapSci.check_captcha()
#     while (has_captcha and has_iframe):
#         captcha_img = ScrapSci.get_captcha_img()
#         captcha_img.show()
#         captcha_text = input("\tPut captcha:\n\t")
#         has_captcha, has_iframe = ScrapSci.solve_captcha(captcha_text)

#     if has_iframe:
#         found, r = ScrapSci.download()

#     found = has_iframe
#     return has_iframe, r
download_link = driver.find_element_by_id(sci_url)
session = requests.Session()
cookies = driver.get_cookies()

for cookie in cookies:
    session.cookies.set(cookie['name'], cookie['value'])
response = session.get(download_link)
