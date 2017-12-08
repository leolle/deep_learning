# -*- coding: utf-8 -*-
import numpy as np
from gensim.models import word2vec
from gensim.models import KeyedVectors
from gensim.models.phrases import Phrases
import os
import itertools
import textract
from textblob import TextBlob

text = '''
The titular threat of The Blob has always struck me as the ultimate movie
monster: an insatiably hungry, amoeba-like mass able to penetrate
virtually any safeguard, capable of--as a doomed doctor chillingly
describes it--"assimilating flesh on contact.
Snide comparisons to gelatin be damned, it's a concept with the most
devastating of potential consequences, not unlike the grey goo scenario
proposed by technological theorists fearful of
artificial intelligence run rampant.
'''

import logging
logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

cur_dir = os.getcwd()
glove_path = '/home/weiwu/share'
name = 'computer_age_statis.pdf'
file_name = os.path.join(cur_dir + '/data/docs/', name)
txt_file = os.path.join(cur_dir, name)


def pdf2text(file_path):
    text = textract.process(file_path)
    return text


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


# text = pdfparser(file_name)
# blob = TextBlob(text)
sentences = word2vec.Text8Corpus('text8')
# sentences = list(blob.noun_phrases)
model = word2vec.Word2Vec(sentences, size=200)
# model.most_similar(positive=['woman', 'king'], negative=['man'], topn=1)
# model.most_similar(positive=['woman', 'king'], negative=['man'], topn=2)
model.most_similar(['titular'])
# model.save('text8.model')
# model.wv.save_word2vec_format('text.model.bin', binary=True)

# more_examples = ["he is she", "big bigger bad", "going went being"]
# for example in more_examples:
#     a, b, x = example.split()
#     predicted = model.most_similar([x, b], [a])[0][0]
#     print("'%s' is to '%s' as '%s' is to '%s'" % (a, b, x, predicted))
