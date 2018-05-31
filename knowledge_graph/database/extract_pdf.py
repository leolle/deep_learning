# -*- coding: utf-8 -*-
# from PyPDF2 import PdfFileReader
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument

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

path = '/home/weiwu/share/deep_learning/docs/knowledge_graph/15. Entity Linking for Biomedical Literature.pdf'
path = '/home/weiwu/share/deep_learning/docs/word_embedding/Distributed Representations of Words and Phrases.pdf'
with open(path, 'rb') as f:
    # pdf = PdfFileReader(f)
    # info = pdf.getDocumentInfo()
    parser = PDFParser(f)
    doc = PDFDocument(parser)
    print(doc.info)
