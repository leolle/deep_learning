# -*- coding: utf-8 -*-
from PyPDF2 import PdfFileReader


def get_info(path):
    with open(path, 'rb') as f:
        pdf = PdfFileReader(f)
        info = pdf.getDocumentInfo()
        number_of_pages = pdf.getNumPages()

    print(info)

    author = info.author
    creator = info.creator
    producer = info.producer
    subject = info.subject
    title = info.title


def text_extractor(path):
    with open(path, 'rb') as f:
        pdf = PdfFileReader(f)

        # get the first page
        page = pdf.getPage(1)
        print(page)
        print('Page type: {}'.format(str(type(page))))

        text = page.extractText()
        print(text)


path = '/home/weiwu/share/deep_learning/docs/knowledge_graph/15. Entity Linking for Biomedical Literature.pdf'
get_info(path)
with open(path, 'rb') as f:
    pdf = PdfFileReader(f)
    info = pdf.getDocumentInfo()
