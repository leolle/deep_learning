# -*- coding: utf-8 -*-
# from PyPDF2 import PdfFileReader
from scihub2pdf import download as dl
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from crossref.restful import Works
from PyPDF2 import PdfFileReader
import re
from ylib import ylog
import logging
from difflib import SequenceMatcher
import bibtexparser
ylog.set_level(logging.DEBUG)
ylog.console_on()
ylog.filelog_on("app")

works = Works()

title = """Adaptive: Focused Crawling"""
w1 = works.query(title).sort('relevance').order('desc')
i = 0
items = None
for item in w1:
    i = i + 1
    t = item['title'][0]
    ylog.debug(item['title'])
    if SequenceMatcher(a=title, b=t).quick_ratio() > 0.9:
        items = item
    if i > 20:
        break
        # items.append(item)
dl.download_from_doi(items['DOI'])
with open('/home/weiwu/share/deep_learning/data/My Collection.bib'
         ) as bibtex_file:
    bib_database = bibtexparser.load(bibtex_file)
items = []
for article in bib_database.entries:
    if article['ENTRYTYPE'] == 'article':
        if article.get('doi') is not None:
            title = article['title'][1:-1]
            # title = ' '.join(['+' + x for x in title.split()])
            ylog.info(title)
            result = {'target': title}
            w1 = works.query(title).sort('relevance').order('desc')
            i = 0
            for item in w1:
                i = i + 1
                try:
                    t = item.get('title')[0]
                except:
                    continue
                if SequenceMatcher(a=title, b=t).quick_ratio() > 0.8:
                    result['result'] = item['title']
                    # ylog.debug(t)
                    break
                if i > 18:
                    ylog.debug('[x]%s' % title)
                    # ylog.debug(item['title'])
                    break
            items.append(result)

counter = 0
ylog.debug('items not found:')
for i in items:
    if i.get('result') is not None:
        counter = counter + 1
    else:
        ylog.debug(i.get('target'))
ylog.debug('#items found: %s' % counter)

for article in bib_database.entries:
    if article['ENTRYTYPE'] == 'article':
        if article.get('doi') is not None:
            i = i + 1
# from crossref.restful import Works, Etiquette

# my_etiquette = Etiquette('My Project Name', 'My Project version',
#                          'My Project URL', 'My contact email')

# str(my_etiquette)

# my_etiquette = Etiquette('My Project Name', '0.2alpha',
#                          'https://myalphaproject.com',
#                          'anonymous@myalphaproject.com')

# str(my_etiquette)

# works = Works(etiquette=my_etiquette)

# for i in works.sample(5).select('DOI'):
#     print(i)
# import os
# from urllib.request import Request, urlopen, HTTPError, URLError

# def download_url(url):
#     try:
#         fn = url.split("/")[-1]
#         fn_download = os.path.join(output_directory, fn)
#         with open(fn_download, "wb") as f:
#             request = Request(sanitize_url(url))
#             request.add_header("User-Agent", "Mozilla/5.0 (compatible; "
#                                "MSIE 9.0; Windows NT 6.1; Trident/5.0)")
#             response = urlopen(request, context=ssl_unverified_context)
#             status_code = response.getcode()
#             if status_code == 200:
#                 f.write(urlopen(request).read())
#                 colorprint(OKGREEN, "Downloaded '%s' to '%s'" % (url,
#                                                                  fn_download))
#             else:
#                 colorprint(FAIL, "Error downloading '%s' (%s)" % (url,
#                                                                   status_code))
#     except HTTPError as e:
#         colorprint(FAIL, "Error downloading '%s' (%s)" % (url, e.code))
#     except URLError as e:
#         colorprint(FAIL, "Error downloading '%s' (%s)" % (url, e.reason))
#     except Exception as e:
#         colorprint(FAIL, "Error downloading '%s' (%s)" % (url, str(e)))
