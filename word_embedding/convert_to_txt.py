# -*- coding: utf-8 -*-
import os
from os.path import join, getsize

for root, dirs, files in os.walk('/home/weiwu/share/deep_learning/data/test'):
    print(root, "consumes, ")
    print(sum([getsize(join(root, name)) for name in files]), '\s')
    print("bytes in", len(files), "non-directory files")

from subprocess import Popen, PIPE
from docx import opc, text

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from cStringIO import StringIO


def convert_pdf_to_txt(path):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = file(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos = set()
    for page in PDFPage.get_pages(
            fp,
            pagenos,
            maxpages=maxpages,
            password=password,
            caching=caching,
            check_extractable=True):
        interpreter.process_page(page)
    fp.close()
    device.close()
    str = retstr.getvalue()
    retstr.close()
    return str


def document_to_text(filename, file_path):
    if filename[-4:] == ".doc":
        cmd = ['antiword', file_path]
        p = Popen(cmd, stdout=PIPE)
        stdout, stderr = p.communicate()
        return stdout.decode('ascii', 'ignore')
    # elif filename[-5:] == ".docx":
    #     document = opc(file_path)
    #     paratextlist = getdocumenttext(document)
    #     newparatextlist = []
    #     for paratext in paratextlist:
    #         newparatextlist.append(paratext.encode("utf-8"))
    #     return '\n\n'.join(newparatextlist)
    elif filename[-4:] == ".odt":
        cmd = ['odt2txt', file_path]
        p = Popen(cmd, stdout=PIPE)
        stdout, stderr = p.communicate()
        return stdout.decode('ascii', 'ignore')
    elif filename[-4:] == ".pdf":
        return convert_pdf_to_txt(file_path)


import sys
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import XMLConverter, HTMLConverter, TextConverter
from pdfminer.layout import LAParams
from cStringIO import StringIO


def pdfparser(data):

    fp = file(data, 'rb')
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    # Create a PDF interpreter object.
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    # Process each page contained in the document.

    for page in PDFPage.get_pages(fp):
        interpreter.process_page(page)
        data = retstr.getvalue()
    return data


filename, file_path = 'Chapter 1.doc', '/home/weiwu/share/deep_learning/data/test'
document_to_text('Chapter 1.doc', '/home/weiwu/share/deep_learning/data/test/')
