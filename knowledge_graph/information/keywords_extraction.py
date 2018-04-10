# -*- coding: utf-8 -*-
import pandas as pd
from pymongo import MongoClient
import gridfs
import sys
import six
import pdfminer.settings
from pdfminer.image import ImageWriter
import pdfminer.layout
import pdfminer.high_level
from gensim import utils
import os
import math
import networkx as nx
import numpy as np
import jieba.posseg as pseg
import codecs
from tempfile import gettempdir
stopwords_path = '/home/weiwu/share/deep_learning/code/stopwords'
user_dict_path = '/home/weiwu/share/deep_learning/data/dict/jieba.txt'
import jieba
jieba.load_userdict(user_dict_path)

tmp_dir = gettempdir()
pdfminer.settings.STRICT = False
try:
    reload(sys)
    sys.setdefaultencoding('utf-8')
except:
    pass
PY2 = sys.version_info[0] == 2
if not PY2:
    # Python 3.x and up
    text_type = str
    string_types = (str,)
    xrange = range

    def as_text(v):  ## 生成unicode字符串
        if v is None:
            return None
        elif isinstance(v, bytes):
            return v.decode('utf-8', errors='ignore')
        elif isinstance(v, str):
            return v
        else:
            raise ValueError('Unknown type %r' % type(v))

    def is_text(v):
        return isinstance(v, text_type)

else:
    # Python 2.x
    text_type = unicode
    string_types = (str, unicode)
    xrange = xrange

    def as_text(v):
        if v is None:
            return None
        elif isinstance(v, unicode):
            return v
        elif isinstance(v, str):
            return v.decode('utf-8', errors='ignore')
        else:
            raise ValueError('Invalid type %r' % type(v))

    def is_text(v):
        return isinstance(v, text_type)


__DEBUG = None

x0 = 'D6B8F9A4422036868574F4DB43BEFEA4'
mg = MongoClient('mongodb://172.16.103.134:27017/')
fs_db = mg['binData']
fs = gridfs.GridFS(fs_db)
print('reading file from mongodb')
result_cursor = fs.find({'filename': x0}, no_cursor_timeout=True)
if result_cursor.count() == 1:
    find_file = result_cursor.next()

fp = open(tmp_dir + '/text.pdf', 'wb')
fp.write(find_file.read())
fp.close()

fp = tmp_dir + '/text.pdf'
fout = tmp_dir + '/text.txt'


def extract_text(
        files=[],
        outfile='-',
        _py2_no_more_posargs=None,  # Bloody Python2 needs a shim
        no_laparams=False,
        all_texts=None,
        detect_vertical=None,  # LAParams
        word_margin=None,
        char_margin=None,
        line_margin=None,
        boxes_flow=None,  # LAParams
        output_type='text',
        codec='utf-8',
        strip_control=False,
        maxpages=0,
        page_numbers=None,
        password="",
        scale=1.0,
        rotation=0,
        layoutmode='normal',
        output_dir=None,
        debug=False,
        disable_caching=False,
        **other):
    if _py2_no_more_posargs is not None:
        raise ValueError("Too many positional arguments passed.")
    if not files:
        raise ValueError("Must provide files to work upon!")

    # If any LAParams group arguments were passed, create an LAParams object and
    # populate with given args. Otherwise, set it to None.
    if not no_laparams:
        laparams = pdfminer.layout.LAParams()
        for param in ("all_texts", "detect_vertical", "word_margin",
                      "char_margin", "line_margin", "boxes_flow"):
            paramv = locals().get(param, None)
            if paramv is not None:
                setattr(laparams, param, paramv)
    else:
        laparams = None

    imagewriter = None
    if output_dir:
        imagewriter = ImageWriter(output_dir)

    if output_type == "text" and outfile != "-":
        for override, alttype in ((".htm", "html"), (".html", "html"),
                                  (".xml", "xml"), (".tag", "tag")):
            if outfile.endswith(override):
                output_type = alttype

    if outfile == "-":
        outfp = sys.stdout
        if outfp.encoding is not None:
            codec = 'utf-8'
    else:
        outfp = open(outfile, "wb")

    for fname in files:
        with open(fname, "rb") as fp:
            pdfminer.high_level.extract_text_to_fp(fp, **locals())
    return outfp


def convert_pdf2txt(args=None):
    import argparse
    P = argparse.ArgumentParser(description=__doc__)
    P.add_argument(
        "files", type=str, default=None, nargs="+", help="Files to process.")
    P.add_argument(
        "-d",
        "--debug",
        default=False,
        action="store_true",
        help="Debug output.")
    P.add_argument(
        "-p",
        "--pagenos",
        type=str,
        help=
        "Comma-separated list of page numbers to parse. Included for legacy applications, use -P/--page-numbers for more idiomatic argument entry."
    )
    P.add_argument(
        "--page-numbers",
        type=int,
        default=None,
        nargs="+",
        help=
        "Alternative to --pagenos with space-separated numbers; supercedes --pagenos where it is used."
    )
    P.add_argument(
        "-m", "--maxpages", type=int, default=0, help="Maximum pages to parse")
    P.add_argument(
        "-P",
        "--password",
        type=str,
        default="",
        help="Decryption password for PDF")
    P.add_argument(
        "-o",
        "--outfile",
        type=str,
        default="-",
        help="Output file (default/'-' is stdout)")
    P.add_argument(
        "-t",
        "--output_type",
        type=str,
        default="text",
        help="Output type: text|html|xml|tag (default is text)")
    P.add_argument(
        "-c", "--codec", type=str, default="utf-8", help="Text encoding")
    P.add_argument("-s", "--scale", type=float, default=1.0, help="Scale")
    P.add_argument(
        "-A",
        "--all-texts",
        default=None,
        action="store_true",
        help="LAParams all texts")
    P.add_argument(
        "-V",
        "--detect-vertical",
        default=None,
        action="store_true",
        help="LAParams detect vertical")
    P.add_argument(
        "-W",
        "--word-margin",
        type=float,
        default=None,
        help="LAParams word margin")
    P.add_argument(
        "-M",
        "--char-margin",
        type=float,
        default=None,
        help="LAParams char margin")
    P.add_argument(
        "-L",
        "--line-margin",
        type=float,
        default=None,
        help="LAParams line margin")
    P.add_argument(
        "-F",
        "--boxes-flow",
        type=float,
        default=None,
        help="LAParams boxes flow")
    P.add_argument(
        "-Y",
        "--layoutmode",
        default="normal",
        type=str,
        help="HTML Layout Mode")
    P.add_argument(
        "-n",
        "--no-laparams",
        default=False,
        action="store_true",
        help="Pass None as LAParams")
    P.add_argument("-R", "--rotation", default=0, type=int, help="Rotation")
    P.add_argument(
        "-O", "--output-dir", default=None, help="Output directory for images")
    P.add_argument(
        "-C",
        "--disable-caching",
        default=False,
        action="store_true",
        help="Disable caching")
    P.add_argument(
        "-S",
        "--strip-control",
        default=False,
        action="store_true",
        help="Strip control in XML mode")
    A = P.parse_args(args=[fp, '--outfile', fout, '--maxpages', '9'])
    #     A = P.parse_args(args=args)

    if A.page_numbers:
        A.page_numbers = set([x - 1 for x in A.page_numbers])
    if A.pagenos:
        A.page_numbers = set([int(x) - 1 for x in A.pagenos.split(",")])

    imagewriter = None
    if A.output_dir:
        imagewriter = ImageWriter(A.output_dir)

    if six.PY2 and sys.stdin.encoding:
        A.password = A.password.decode(sys.stdin.encoding)

    if A.output_type == "text" and A.outfile != "-":
        for override, alttype in ((".htm", "html"), (".html", "html"),
                                  (".xml", "xml"), (".tag", "tag")):
            if A.outfile.endswith(override):
                A.output_type = alttype

    if A.outfile == "-":
        outfp = sys.stdout
        if outfp.encoding is not None:
            # Why ignore outfp.encoding? :-/ stupid cathal?
            A.codec = 'utf-8'
    else:
        outfp = open(A.outfile, "wb")

    ## Test Code
    outfp = extract_text(**vars(A))
    outfp.close()
    return 0


print('convert pdf to txt')
convert_pdf2txt(args=None)

with open(tmp_dir + '/text.txt', 'rb') as f:
    text = f.read()

s = utils.to_unicode(text)
text = s.replace('\n\n', '')

sentence_delimiters = ['?', '!', ';', '？', '！', '。', '；', '……', '…', '\n']
allow_speech_tags = [
    'an', 'i', 'j', 'l', 'n', 'nr', 'nrfg', 'ns', 'nt', 'nz', 't', 'v', 'vd',
    'vn', 'eng'
]


def debug(*args):
    global __DEBUG
    if __DEBUG is None:
        try:
            if os.environ['DEBUG'] == '1':
                __DEBUG = True
            else:
                __DEBUG = False
        except:
            __DEBUG = False
    if __DEBUG:
        print(' '.join([str(arg) for arg in args]))


class AttrDict(dict):
    """Dict that can get attribute by dot"""

    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


def combine(word_list, window=2):
    """构造在window下的单词组合，用来构造单词之间的边。

    Keyword arguments:
    word_list  --  list of str, 由单词组成的列表。
    windows    --  int, 窗口大小。
    """
    if window < 2: window = 2
    for x in xrange(1, window):
        if x >= len(word_list):
            break
        word_list2 = word_list[x:]
        res = zip(word_list, word_list2)
        for r in res:
            yield r


def get_similarity(word_list1, word_list2):
    """默认的用于计算两个句子相似度的函数。

    Keyword arguments:
    word_list1, word_list2  --  分别代表两个句子，都是由单词组成的列表
    """
    words = list(set(word_list1 + word_list2))
    vector1 = [float(word_list1.count(word)) for word in words]
    vector2 = [float(word_list2.count(word)) for word in words]

    vector3 = [vector1[x] * vector2[x] for x in xrange(len(vector1))]
    vector4 = [1 for num in vector3 if num > 0.]
    co_occur_num = sum(vector4)

    if abs(co_occur_num) <= 1e-12:
        return 0.

    denominator = math.log(float(len(word_list1))) + math.log(
        float(len(word_list2)))  # 分母

    if abs(denominator) < 1e-12:
        return 0.

    return co_occur_num / denominator


def sort_words(vertex_source,
               edge_source,
               window=2,
               pagerank_config={
                   'alpha': 0.85,
               }):
    """将单词按关键程度从大到小排序

    Keyword arguments:
    vertex_source   --  二维列表，子列表代表句子，子列表的元素是单词，这些单词用来构造pagerank中的节点
    edge_source     --  二维列表，子列表代表句子，子列表的元素是单词，根据单词位置关系构造pagerank中的边
    window          --  一个句子中相邻的window个单词，两两之间认为有边
    pagerank_config --  pagerank的设置
    """
    sorted_words = []
    word_index = {}
    index_word = {}
    _vertex_source = vertex_source
    _edge_source = edge_source
    words_number = 0
    for word_list in _vertex_source:
        for word in word_list:
            if not word in word_index:
                word_index[word] = words_number
                index_word[words_number] = word
                words_number += 1

    graph = np.zeros((words_number, words_number))

    for word_list in _edge_source:
        for w1, w2 in combine(word_list, window):
            if w1 in word_index and w2 in word_index:
                index1 = word_index[w1]
                index2 = word_index[w2]
                graph[index1][index2] = 1.0
                graph[index2][index1] = 1.0

    debug('graph:\n', graph)

    nx_graph = nx.from_numpy_matrix(graph)
    nx.write_gexf(nx_graph, tmp_dir + '/graph.gexf')
    scores = nx.pagerank(nx_graph, **pagerank_config)  # this is a dict
    sorted_scores = sorted(
        scores.items(), key=lambda item: item[1], reverse=True)
    for index, score in sorted_scores:
        item = AttrDict(word=index_word[index], weight=score)
        sorted_words.append(item)

    return sorted_words


def sort_sentences(sentences,
                   words,
                   sim_func=get_similarity,
                   pagerank_config={
                       'alpha': 0.85,
                   }):
    """将句子按照关键程度从大到小排序

    Keyword arguments:
    sentences         --  列表，元素是句子
    words             --  二维列表，子列表和sentences中的句子对应，子列表由单词组成
    sim_func          --  计算两个句子的相似性，参数是两个由单词组成的列表
    pagerank_config   --  pagerank的设置
    """
    sorted_sentences = []
    _source = words
    sentences_num = len(_source)
    graph = np.zeros((sentences_num, sentences_num))

    for x in xrange(sentences_num):
        for y in xrange(x, sentences_num):
            similarity = sim_func(_source[x], _source[y])
            graph[x, y] = similarity
            graph[y, x] = similarity

    nx_graph = nx.from_numpy_matrix(graph)
    scores = nx.pagerank(nx_graph, **pagerank_config)  # this is a dict
    sorted_scores = sorted(
        scores.items(), key=lambda item: item[1], reverse=True)

    for index, score in sorted_scores:
        item = AttrDict(index=index, sentence=sentences[index], weight=score)
        sorted_sentences.append(item)

    return sorted_sentences


class WordSegmentation:

    def __init__(self,
                 stop_words_file=None,
                 allow_speech_tags=allow_speech_tags):
        """
        Keyword arguments:
        stop_words_file    -- 保存停止词的文件路径，utf8编码，每行一个停止词。若不是str类型，则使用默认的停止词
        allow_speech_tags  -- 词性列表，用于过滤
        """

        allow_speech_tags = [as_text(item) for item in allow_speech_tags]

        self.default_speech_tag_filter = allow_speech_tags
        self.stop_words = set()
        self.stop_words_file = stopwords_path
        if type(stop_words_file) is str:
            self.stop_words_file = stop_words_file
        for word in codecs.open(self.stop_words_file, 'r', 'utf-8', 'ignore'):
            self.stop_words.add(word.strip())

    def segment(self,
                text,
                lower=True,
                use_stop_words=True,
                use_speech_tags_filter=False):
        """对一段文本进行分词，返回list类型的分词结果

        Keyword arguments:
        lower                  -- 是否将单词小写（针对英文）
        use_stop_words         -- 若为True，则利用停止词集合来过滤（去掉停止词）
        use_speech_tags_filter -- 是否基于词性进行过滤。若为True，则使用self.default_speech_tag_filter过滤。否则，不过滤。
        """
        text = as_text(text)
        jieba_result = pseg.cut(text)

        if use_speech_tags_filter == True:
            jieba_result = [
                w for w in jieba_result
                if w.flag in self.default_speech_tag_filter
            ]
        else:
            jieba_result = [w for w in jieba_result]

        # 去除特殊符号
        word_list = [w.word.strip() for w in jieba_result if w.flag != 'x']
        word_list = [word for word in word_list if len(word) > 0]

        if lower:
            word_list = [word.lower() for word in word_list]

        if use_stop_words:
            word_list = [
                word.strip() for word in word_list
                if word.strip() not in self.stop_words
            ]

        return word_list

    def segment_sentences(self,
                          sentences,
                          lower=True,
                          use_stop_words=True,
                          use_speech_tags_filter=False):
        """将列表sequences中的每个元素/句子转换为由单词构成的列表。

        sequences -- 列表，每个元素是一个句子（字符串类型）
        """

        res = []
        for sentence in sentences:
            res.append(
                self.segment(
                    text=sentence,
                    lower=lower,
                    use_stop_words=use_stop_words,
                    use_speech_tags_filter=use_speech_tags_filter))
        return res


class SentenceSegmentation(object):
    """ 分句 """

    def __init__(self, delimiters=sentence_delimiters):
        """
        Keyword arguments:
        delimiters -- 可迭代对象，用来拆分句子
        """
        self.delimiters = set([as_text(item) for item in delimiters])

    def segment(self, text):
        res = [as_text(text)]

        debug(res)
        debug(self.delimiters)

        for sep in self.delimiters:
            text, res = res, []
            for seq in text:
                res += seq.split(sep)
        res = [s.strip() for s in res if len(s.strip()) > 0]
        return res


class Segmentation(object):

    def __init__(self,
                 stop_words_file=None,
                 allow_speech_tags=allow_speech_tags,
                 delimiters=sentence_delimiters):
        """
        Keyword arguments:
        stop_words_file -- 停止词文件
        delimiters      -- 用来拆分句子的符号集合
        """
        self.ws = WordSegmentation(
            stop_words_file=stop_words_file,
            allow_speech_tags=allow_speech_tags)
        self.ss = SentenceSegmentation(delimiters=delimiters)

    def segment(self, text, lower=False):
        text = as_text(text)
        sentences = self.ss.segment(text)
        words_no_filter = self.ws.segment_sentences(
            sentences=sentences,
            lower=lower,
            use_stop_words=False,
            use_speech_tags_filter=False)
        words_no_stop_words = self.ws.segment_sentences(
            sentences=sentences,
            lower=lower,
            use_stop_words=True,
            use_speech_tags_filter=False)

        words_all_filters = self.ws.segment_sentences(
            sentences=sentences,
            lower=lower,
            use_stop_words=True,
            use_speech_tags_filter=True)

        return AttrDict(
            sentences=sentences,
            words_no_filter=words_no_filter,
            words_no_stop_words=words_no_stop_words,
            words_all_filters=words_all_filters)


class TextRank4Keyword(object):

    def __init__(self,
                 stop_words_file=None,
                 allow_speech_tags=allow_speech_tags,
                 delimiters=sentence_delimiters):
        """
        Keyword arguments:
        stop_words_file  --  str，指定停止词文件路径（一行一个停止词），若为其他类型，则使用默认停止词文件
        delimiters       --  默认值是`?!;？！。；…\n`，用来将文本拆分为句子。

        Object Var:
        self.words_no_filter      --  对sentences中每个句子分词而得到的两级列表。
        self.words_no_stop_words  --  去掉words_no_filter中的停止词而得到的两级列表。
        self.words_all_filters    --  保留words_no_stop_words中指定词性的单词而得到的两级列表。
        """
        self.text = ''
        self.keywords = None

        self.seg = Segmentation(
            stop_words_file=stop_words_file,
            allow_speech_tags=allow_speech_tags,
            delimiters=delimiters)

        self.sentences = None
        self.words_no_filter = None  # 2维列表
        self.words_no_stop_words = None
        self.words_all_filters = None

    def analyze(self,
                text,
                window=2,
                lower=False,
                vertex_source='all_filters',
                edge_source='no_stop_words',
                pagerank_config={
                    'alpha': 0.85,
                }):
        """分析文本

        Keyword arguments:
        text       --  文本内容，字符串。
        window     --  窗口大小，int，用来构造单词之间的边。默认值为2。
        lower      --  是否将文本转换为小写。默认为False。
        vertex_source   --  选择使用words_no_filter, words_no_stop_words, words_all_filters中的哪一个来构造pagerank对应的图中的节点。
                            默认值为`'all_filters'`，可选值为`'no_filter', 'no_stop_words', 'all_filters'`。关键词也来自`vertex_source`。
        edge_source     --  选择使用words_no_filter, words_no_stop_words, words_all_filters中的哪一个来构造pagerank对应的图中的节点之间的边。
                            默认值为`'no_stop_words'`，可选值为`'no_filter', 'no_stop_words', 'all_filters'`。边的构造要结合`window`参数。
        """

        # self.text = as_text(text)
        self.text = text
        self.word_index = {}
        self.index_word = {}
        self.keywords = []
        self.graph = None

        result = self.seg.segment(text=text, lower=lower)
        self.sentences = result.sentences
        self.words_no_filter = result.words_no_filter
        self.words_no_stop_words = result.words_no_stop_words
        self.words_all_filters = result.words_all_filters

        debug(20 * '*')
        debug('self.sentences in TextRank4Keyword:\n',
              ' || '.join(self.sentences))
        debug('self.words_no_filter in TextRank4Keyword:\n',
              self.words_no_filter)
        debug('self.words_no_stop_words in TextRank4Keyword:\n',
              self.words_no_stop_words)
        debug('self.words_all_filters in TextRank4Keyword:\n',
              self.words_all_filters)

        options = ['no_filter', 'no_stop_words', 'all_filters']

        if vertex_source in options:
            _vertex_source = result['words_' + vertex_source]
        else:
            _vertex_source = result['words_all_filters']

        if edge_source in options:
            _edge_source = result['words_' + edge_source]
        else:
            _edge_source = result['words_no_stop_words']

        self.keywords = sort_words(
            _vertex_source,
            _edge_source,
            window=window,
            pagerank_config=pagerank_config)

    def get_keywords(self, num=6, word_min_len=2):
        """获取最重要的num个长度大于等于word_min_len的关键词。

        Return:
        关键词列表。
        """
        result = []
        count = 0
        # print('total keywords')
        # print(len(self.keywords))
        # print('unique keywords')
        # print(len(list(unique_everseen([x.word for x in self.keywords]))))
        fraction = len(self.keywords) // num
        for item in self.keywords:
            if count >= fraction:
                break
            if len(item.word) >= word_min_len:
                result.append(item)
                count += 1
        return result

    def get_keyphrases(self, keywords_num=12, min_occur_num=2):
        """获取关键短语。
        获取 keywords_num 个关键词构造的可能出现的短语，要求这个短语在原文本中至少出现的次数为min_occur_num。

        Return:
        关键短语的列表。
        """
        keywords_set = set([
            item.word
            for item in self.get_keywords(num=keywords_num, word_min_len=1)
        ])
        keyphrases = set()
        for sentence in self.words_no_filter:
            one = []
            for word in sentence:
                if word in keywords_set:
                    one.append(word)
                else:
                    if len(one) > 1:
                        keyphrases.add(''.join(one))
                    if len(one) == 0:
                        continue
                    else:
                        one = []
            # 兜底
            if len(one) > 1:
                keyphrases.add(''.join(one))

        return [
            phrase for phrase in keyphrases
            if self.text.count(phrase) >= min_occur_num
        ]


print('extract keywords')
tr4w = TextRank4Keyword()

tr4w.analyze(
    text=text, lower=True,
    window=2)  # py2中text必须是utf8编码的str或者unicode对象，py3中必须是utf8编码的bytes或者str对象

print('关键词：')
for item in tr4w.get_keywords(10, word_min_len=2):
    print(item.word, item.weight)
