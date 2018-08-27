# -*- coding: utf-8 -*-
"""batch convert research report pdf to txt"""
from pdf_to_txt import p2t
import os
import re
import string
from os.path import join, getsize
from gensim import utils

punctuation = u''':!),.:;?]}¢'"、。〉》」』】〕〗〞︰︱︳﹐､﹒﹔﹕﹖﹗﹚﹜﹞！），．：；？｜｝︴︶︸︺︼︾﹀﹂﹄﹏､～￠々‖•·ˇˉ―--′’”([{£¥'"‵〈《「『【〔〖（［｛￡￥〝︵︷︹︻︽︿﹁﹃﹙﹛﹝（｛“‘-—_…'''
RE_PUNCT = re.compile(r'([%s])+' % re.escape(punctuation + string.punctuation),
                      re.UNICODE)
RE_TAGS = re.compile(r"<([^>]+)>", re.UNICODE)
RE_NUMERIC = re.compile(r"[0-9]+", re.UNICODE)
RE_NONALPHA = re.compile(r"\W", re.UNICODE)
RE_WHITESPACE = re.compile(r"(\s)+", re.UNICODE)
RE_NONSENSE = re.compile(
    r"[^!#$%&'()*+,-./:;<=>?@[\]^_`{|}~\u4e00-\u9fa5a-zA-Z0-9\u3002\uff1b\uff0c\uff1a\u201c\u201d\uff08\uff09\u3001\uff1f\u300a\u300b\n\s]+",
    re.UNICODE)
RE_L = re.compile("\u000C", re.UNICODE)

pdf_path = '/home/weiwu/share/deep_learning/docs/1_macro_economy/'
for (root, dirs, files) in os.walk(pdf_path):
    for filename in files:
        file_path = join(root, filename)
        if file_path.endswith('.pdf'):
            print(file_path)
            fout = file_path[:-3] + 'txt'
            try:
                p2t(file_path, fout, None)
            except:
                continue
            with open(fout, 'r') as fp:
                text = fp.read()
                s = utils.to_unicode(text)
                text = s.replace('\n\n', '')
            with open(fout, 'w') as f:
                f.write(text)
