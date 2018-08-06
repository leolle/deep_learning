# -*- coding: utf-8 -*-
'''extract doi from pdf, fetch metadata from crossref.org'''
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

title = """Heterogeneous resistance to vancomycin in Staphylococcus epidermidis, Staphylococcus haemolyticus and Staphylococcus warneri clinical strains: characterisation"""
w1 = works.query(title).sort('relevance').order('desc')
i = 0
target_doi = '10.1109/icdcs.2006.48'
items_result = None
for item in w1:
    i = i + 1
    try:
        t = item.get('title')[0]
        sub_title = item.get('subtitle')[0]
        ylog.debug('crossref item title ')
        ylog.debug(t)
        ylog.debug(sub_title)
    except:
        ylog.debug(item)
        continue
    if SequenceMatcher(a=title, b=t).ratio() > 0.8:
        found_doi = item['DOI']
        ylog.debug("target doi: %s" % target_doi)
        ylog.debug("found  doi: %s" % found_doi)
        if target_doi[:10] == found_doi[:10] or SequenceMatcher(
                a=target_doi, b=found_doi).ratio() > 0.9:
            print('found')
            break
    if i > 0:
        ylog.debug('[x]%s' % title)
        # ylog.debug(item['title'])
        break

dl.download_from_doi('10.1145/2449396.2449413')

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
                if SequenceMatcher(a=title, b=t).ratio() > 0.9:
                    result['result'] = item['title']
                    target_doi = article.get('doi').lower()
                    found_doi = item['DOI'].lower()
                    ylog.debug("target doi: %s" % target_doi)
                    ylog.debug("found  doi: %s" % found_doi)
                    if target_doi in found_doi or SequenceMatcher(
                            a=target_doi, b=found_doi).ratio() > 0.9:
                        break
                if i > 18:
                    ylog.debug('[x]%s' % title)
                    # ylog.debug(item['title'])
                    break
            items.append(result)


def find_meta(title, doi):
    """ find metadata with title or doi
    Keyword Arguments:
    title --
    doi   --
    """
    ylog.info(title)
    works = Works()
    w1 = works.query(title).sort('relevance').order('desc')
    i = 0
    for item in w1:
        i = i + 1
        try:
            t = item.get('title')[0]
            sub_title = item.get('subtitle')[0]
        except:
            continue
        if SequenceMatcher(
                a=title, b=t).ratio() > 0.9 or SequenceMatcher(
                    a=title, b=sub_title).ratio > 0.9:
            return item
        if i > 18:
            ylog.debug('[x]%s' % title)
            # ylog.debug(item['title'])
            return None


counter = 0
ylog.debug('items not found:')
for i in items:
    if i.get('result') is not None:
        counter = counter + 1
    else:
        ylog.debug(i.get('target'))
ylog.debug('#items found: %s' % counter)

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
title = """Heterogeneous resistance to vancomycin in Staphylococcus epidermidis, Staphylococcus haemolyticus and Staphylococcus warneri clinical strains: characterisation"""
w1 = works.query(title).sort('relevance').order('desc')
i = 0
target_doi = '10.1109/icdcs.2006.48'
items_result = None
for item in w1:
    i = i + 1
    t = item.get('title')[0]
    sub_title = item.get('subtitle')[0]
    ylog.debug('crossref item title ')
    ylog.debug(t)
    ylog.debug(sub_title)
    ylog.debug(item)
    if SequenceMatcher(a=title, b=t).ratio() > 0.8:
        found_doi = item['DOI']
        ylog.debug("target doi: %s" % target_doi)
        ylog.debug("found  doi: %s" % found_doi)
        if target_doi[:10] == found_doi[:10] or SequenceMatcher(
                a=target_doi, b=found_doi).ratio() > 0.9:
            print('found')
            break
    if i > 0:
        ylog.debug('[x]%s' % title)
        # ylog.debug(item['title'])
        break

import subprocess
import os


def grobid(pdf_folder, grobid_home=None, grobid_jar=None):
    """
    Run `Grobid <https://github.com/kermitt2/grobid>`_ on a given folder to \
            extract references.
    .. note::
        Before using this function, you have to download and build Grobid on \
                your system. See \
                `<https://grobid.readthedocs.org/en/latest/Install-Grobid/>`_ \
                for more infos on this. You need Java to be in your ``$PATH``.
    :param pdf_folder: Folder containing the PDF files to handle.
    :param grobid_home: Path to the grobid-home directory.
    :param grobid_jar: Path to the built Grobid JAR file.
    :returns: ``True``, or ``False`` if an error occurred.
    """
    # TODO: Should be using https://github.com/kermitt2/grobid-example and
    # BibTeX backend.
    if grobid_home is None or grobid_jar is None:
        # User should pass the correct paths
        return False

    try:
        subprocess.call([
            "java",
            "-jar",
            grobid_jar,
            # Avoid OutOfMemoryException
            "-Xmx1024m",
            "-gH",
            grobid_home,
            "-gP",
            os.path.join(grobid_home, "config/grobid.properties"),
            "-dIn",
            pdf_folder,
            "-exe",
            "processReferences"
        ])
        return True
    except subprocess.CalledProcessError:
        return False


curl_string = """
curl -v --form input=@/home/weiwu/share/deep_learning/docs/github/zhang2016.pdf --form teiCoordinates=persName --form teiCoordinates=figure --form teiCoordinates=ref --form teiCoordinates=biblStruct --form teiCoordinates=formula localhost:8070/api/processFulltextDocument
"""
