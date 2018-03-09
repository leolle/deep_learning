#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
"""
import logging
import os
import re
import sys
import codecs
import itertools
import multiprocessing
import string
from sys import stdin
import glob
user_path = os.path.expanduser("~")
import jieba
jieba.load_userdict(user_path + "/share/deep_learning/data/dict/jieba.txt")

import gensim
from gensim import utils
import logging

logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

punctuation = u''':!),.:;?]}¢'"、。〉》」』】〕〗〞︰︱︳﹐､﹒﹔﹕﹖﹗﹚﹜﹞！），．：；？｜｝︴︶︸︺︼︾﹀﹂﹄﹏､～￠々‖•·ˇˉ―--′’”([{£¥'"‵〈《「『【〔〖（［｛￡￥〝︵︷︹︻︽︿﹁﹃﹙﹛﹝（｛“‘-—_…'''
STOPWORDS = codecs.open('stopwords', 'r', 'utf-8').read().split()


def complete_dir_path(dir_path):
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
    if not dir_path.endswith('/'):
        return dir_path + '/'
    else:
        return dir_path


RE_PUNCT = re.compile(r'([%s])+' % re.escape(punctuation + string.punctuation),
                      re.UNICODE)
RE_TAGS = re.compile(r"<([^>]+)>", re.UNICODE)
RE_NUMERIC = re.compile(r"[0-9]+", re.UNICODE)
RE_NONALPHA = re.compile(r"\W", re.UNICODE)
RE_WHITESPACE = re.compile(r"(\s)+", re.UNICODE)


def remove_stopwords(s):
    """Remove :STOPWORDS from `s`.

    Parameters
    ----------
    s : str

    Returns
    -------
    str
        Unicode string without :STOPWORDS.

    EXAMPLES
    --------
    >>> from gensim.parsing.preprocessing import remove_stopwords
    >>> remove_stopwords(u"一般使用的单位是每平方公里人数或每平方米所居住的人口数。")
    u'使用单位平方公里人数每平方米居住人口数。'

    """
    s = utils.to_unicode(s)
    tokens_generator = jieba.cut(s)
    return "".join(w for w in tokens_generator if w not in STOPWORDS)


def strip_punctuation(s):
    """Replace punctuation characters with spaces in `s` using :const:`RE_PUNCT`.

    Parameters
    ----------
    s : str

    Returns
    -------
    str
        Unicode string without punctuation characters.

    Examples
    --------
    >>> from wiki_preprocess import strip_punctuation
    >>> strip_punctuation("通常用于计算一个国家、地区、城市全球人口分布状况。")
    u'它通常用于计算一个国家 地区 城市或全球的人口分布状况 '
    >>> strip_punctuation("A semicolon is a stronger break than a comma, but not as much as a full stop!")
    u'A semicolon is a stronger break than a comma  but not as much as a full stop '
    """
    s = utils.to_unicode(s)
    return RE_PUNCT.sub(" ", s)


def strip_numeric(s):
    """Remove digits from `s` using :const:`RE_NUMERIC`.

    Parameters
    ----------
    s : str

    Returns
    -------
    str
        Unicode  string without digits.

    Examples
    --------
    >>> from wiki_preprocess import strip_numeric
    >>> strip_numeric("0text24gensim365test")
    u'textgensimtest'
    >>> strip_numeric(u"原子核(atomic nucleus)，占了99.96%以上原子的质量。它的直径在10-12至10-13公分之间,1912年")
    u"原子核(atomic nucleus)，占了.%以上原子的质量。它的直径在-至-公分之间,年"
    """
    s = utils.to_unicode(s)
    # tokens_generator = jieba.cut(s)
    # return "".join(w for w in tokens_generator if w not in STOPWORDS)
    return RE_NUMERIC.sub("", s)


def cut_paragraph(s):
    """cut pages to paragraph.
    Keyword Arguments:
    s -- string
    """
    s = utils.to_unicode(s)
    return '\n'.join(s.split())


def cut_article(s):
    """join pages to a whole document.
    Keyword Arguments:
    s -- string
    """
    s = utils.to_unicode(s)
    return ''.join(s.split())


def tokenize(s):
    """Remove :tokenize from `s`.

    Parameters
    ----------
    s : str

    Returns
    -------
    str
        Unicode string with phrase.

    EXAMPLES
    --------
    >>> from gensim.parsing.preprocessing import remove_stopwords
    >>> remove_stopwords(u"u'使用单位平方公里人数每平方米居住人口数。'")
    u"使用 单位 平方公里 人数 每平方米 居住 人口数。"

    """
    s = utils.to_unicode(s)
    tokens_generator = jieba.cut(s)
    return " ".join(w for w in tokens_generator)


DEFAULT_FILTERS = [
    cut_article, strip_numeric, remove_stopwords, strip_punctuation, tokenize
]


def preprocess_string(s, filters=DEFAULT_FILTERS):
    """Apply list of chosen filters to `s`.

    Default list of filters:

    * :func:`preprocessing.strip_punctuation`,
    * :func:`preprocessing.strip_numeric`,
    * :func:`preprocessing.remove_stopwords`,

    Parameters
    ----------
    s : str
    filters: list of functions, optional

    Returns
    -------
    list of str
        Processed strings (cleaned).

    Examples
    --------
    >>> preprocessing import preprocess_string
    >>> preprocess_string("<i>Hel 9lo</i> <b>Wo9 rld</b>! Th3     weather_is really g00d today, isn't it?")
    [u'hel', u'rld', u'weather', u'todai', u'isn']
    >>>
    >>> s = "<i>Hel 9lo</i> <b>Wo9 rld</b>! Th3     weather_is really g00d today, isn't it?"
    >>> CUSTOM_FILTERS = [lambda x: x.lower(), strip_tags, strip_punctuation]
    >>> preprocess_string(s, CUSTOM_FILTERS)
    [u'hel', u'9lo', u'wo9', u'rld', u'th3', u'weather', u'is', u'really', u'g00d', u'today', u'isn', u't', u'it']

    """
    s = utils.to_unicode(s)
    for f in filters:
        s = f(s)
    return s
