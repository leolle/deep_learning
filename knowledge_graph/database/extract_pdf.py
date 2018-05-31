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

ylog.set_level(logging.DEBUG)
ylog.console_on()
ylog.filelog_on("app")

works = Works()

title = """Neural Architectures for Named Entity Recognition"""
w1 = works.query(title).sort('relevance').order('desc')
i = 0
items = None
for item in w1:
    i = i + 1
    if i > 20:
        break
    ylog.debug(item['title'])
    t = item['title'][0]
    if SequenceMatcher(a=title, b=t).quick_ratio() > 0.9:
        items = item
        # items.append(item)
dl.download_from_doi(items['DOI'])

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
import os
from urllib.request import Request, urlopen, HTTPError, URLError


def download_url(url):
    try:
        fn = url.split("/")[-1]
        fn_download = os.path.join(output_directory, fn)
        with open(fn_download, "wb") as f:
            request = Request(sanitize_url(url))
            request.add_header("User-Agent", "Mozilla/5.0 (compatible; "
                               "MSIE 9.0; Windows NT 6.1; Trident/5.0)")
            response = urlopen(request, context=ssl_unverified_context)
            status_code = response.getcode()
            if status_code == 200:
                f.write(urlopen(request).read())
                colorprint(OKGREEN, "Downloaded '%s' to '%s'" % (url,
                                                                 fn_download))
            else:
                colorprint(FAIL, "Error downloading '%s' (%s)" % (url,
                                                                  status_code))
    except HTTPError as e:
        colorprint(FAIL, "Error downloading '%s' (%s)" % (url, e.code))
    except URLError as e:
        colorprint(FAIL, "Error downloading '%s' (%s)" % (url, e.reason))
    except Exception as e:
        colorprint(FAIL, "Error downloading '%s' (%s)" % (url, str(e)))


# Create directory
if not os.path.exists(output_directory):
    os.makedirs(output_directory)
    vprint("Created directory '%s'" % output_directory)

try:
    pool = ThreadPool(5)
    pool.map(download_url, urls)
    pool.wait_completion()

except Exception as e:
    print(e)
except KeyboardInterrupt:
    pass
