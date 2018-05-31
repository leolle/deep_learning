# -*- coding: utf-8 -*-
# from PyPDF2 import PdfFileReader
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
# def get_info(path):
#     with open(path, 'rb') as f:
#         pdf = PdfFileReader(f)
#         info = pdf.getDocumentInfo()
#         number_of_pages = pdf.getNumPages()

#     print(info)

#     author = info.author
#     creator = info.creator
#     producer = info.producer
#     subject = info.subject
#     title = info.title

# def text_extractor(path):
#     with open(path, 'rb') as f:
#         pdf = PdfFileReader(f)

#         # get the first page
#         page = pdf.getPage(1)
#         print(page)
#         print('Page type: {}'.format(str(type(page))))

#         text = page.extractText()
#         print(text)

# get_info(path)

path = '/home/weiwu/share/deep_learning/docs/word_embedding/Distributed Representations of Words and Phrases.pdf'
path = '/home/weiwu/share/deep_learning/docs/knowledge_graph/15. Entity Linking for Biomedical Literature.pdf'
with open(path, 'rb') as f:
    # pdf = PdfFileReader(f)
    # info = pdf.getDocumentInfo()
    parser = PDFParser(f)
    doc = PDFDocument(parser)
    print(doc.info)

works = Works()
print(works.doi('10.1021/ma035065b'))

# w1 = works.query(
#     title='zika', author='johannes', publisher_name='Wiley-Blackwell')
title = """Neural Architectures for Named Entity Recognition"""
w1 = works.query(title).sort('relevance').order('desc').filter(
    has_abstract='true')
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

from crossref.restful import Works, Etiquette

my_etiquette = Etiquette('My Project Name', 'My Project version',
                         'My Project URL', 'My contact email')

str(my_etiquette)

my_etiquette = Etiquette('My Project Name', '0.2alpha',
                         'https://myalphaproject.com',
                         'anonymous@myalphaproject.com')

str(my_etiquette)

works = Works(etiquette=my_etiquette)

for i in works.sample(5).select('DOI'):
    print(i)
# doi_re = re.compile("10.(\d)+/([^(\s\>\"\<)])+")

# with open(path, 'rb') as f:
#       pdf = PdfFileReader(f)
#       text = pdf.getPage(1).extractText()
#       m = doi_re.search(text)
#       print(m.group(0))

# from refextract import extract_references_from_file
# references = extract_references_from_file(path)
# print(references[0])
