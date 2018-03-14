#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
fetch all the page from field csv files, pack them to a file.
fetch skill gid and extract page.
python wiki_preprocess.py > zh.wiki.docs
"""
import gensim
import logging
import multiprocessing
import os
import sys
from time import time
from gensim.models.word2vec import LineSentence
from fetch import extract_pages
# from ylib import ylog
from preprocessing import complete_dir_path
from lib.gftTools import gftIO

# test fetch graph
prod_url = 'http://q.gftchina.com:13567'
prod_url_bck = 'http://172.16.103.106:9080'
test_user_name = 'wuwei'
test_pwd = 'gft'
gs_call = gftIO.GSCall(prod_url, test_user_name, test_pwd)


def skill_extraction(skill_gid, key, key_string, target_key, gs_call):
    """ extract skill instance and get graph nodes gid
    1. extract skill instance to get graph
    2. parse graph to get nodes gid
    graph structure:
    graphs {
      graph {
        nodes {
          node_prop {
            props {
              entries {
                key: "_gid"
                value: "D39BB7BF0E3FFEB5CC8E4135EA9D5ED4"
              }
              entries {
                key: "_type"
                value: "readonlyDoc"
              }
              entries {
                key: "url"
                value: "https://zh.wikipedia.org/wiki/%E6%B1%89%E5%A0%A1%E8%AF%81%E5%88%B8%E4%BA%A4%E6%98%93%E6%89%80"
              }
            }
          }
        }
      }
    }
    Keyword Arguments:
    skill_gid  -- skill instance gid
    key        -- source key
    key_string -- source key value
    target_key -- target key
    """
    graph = gs_call.get_graph_from_neo4j(skill_gid)
    ls_extract = []
    for g in graph.graphs:
        dict_node = {}
        for i in g.graph.nodes:
            # print(i.node_prop.props.entries)
            for e in i.node_prop.props.entries:
                dict_node[e.key] = e.value
                # print(dict_node)
            if dict_node[key] == key_string:
                ls_extract.append(dict_node[target_key])
    return ls_extract


# if __name__ == '__main__':

# ylog.set_level(logging.DEBUG)
# ylog.console_on()
# ylog.filelog_on("wiki_train")
# ylog.info("start")
logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

begin = time()
user_path = os.path.expanduser("~")
page_gid = skill_extraction('A0F920E1D1DB9E6EFD378FD1B9200461', '_type',
                            'readonlyDoc', '_gid', gs_call)
# output_path = sys.argv[1]

extract_pages(page_gid, gs_call)
logging.info("start training")
model = gensim.models.Word2Vec(
    LineSentence('/tmp/test.txt'),
    size=200,
    window=5,
    min_count=2,
    workers=multiprocessing.cpu_count())
# model.wv.save_word2vec_format(
#     complete_dir_path(output_path) + "wiki.w2v_org",
#     complete_dir_path(output_path) + "wiki.vocab",
#     binary=False)
end = time()
load_duration = end - begin
logging.info("Total procesing time: %d seconds" % (end - begin))

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
fetch skill gid and extract page.
preprocess text, remove punctuation, remove stopwords, tokenize.
train word2vec model.
save model.
"""
import gensim
import logging
import multiprocessing
import os
import sys
from time import time
from gensim.models.word2vec import LineSentence
# from ylib import ylog
from lib.gftTools import gftIO
from lib.gftTools.word2Vec import preprocessing
from google.protobuf.message import DecodeError

# test fetch graph
prod_url = 'http://172.16.103.106:9080'
test_user_name = 'wuwei'
test_pwd = 'gft'
gs_call = gftIO.GSCall(prod_url, test_user_name, test_pwd)


def complete_dir_path(dir_path):
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
    if not dir_path.endswith('/'):
        return dir_path + '/'
    else:
        return dir_path


def extract_pages(ls_pageid, gs_call):
    """ Extract nodes read only documents from input list of gid,
    preprocess text, remove punctuation, remove stopwords, tokenize.
    """
    from tempfile import gettempdir
    tmp_dir = gettempdir()
    output = open(tmp_dir + '/test.txt', 'wb')
    logging.info("extract pages")
    if isinstance(ls_pageid, list):
        for page_id in ls_pageid:
            logging.info(page_id)
            try:
                text = gs_call.get_nodes_binary_data([page_id])
            except DecodeError:
                continue
            page = text.entries[0].data.data.decode('utf-8')
            text = preprocessing.preprocess_string(page)
            # ylog.debug(text)
            output.write(text.encode('utf-8'))
            output.write('\n'.encode('utf-8'))
    elif isinstance(ls_pageid, gftIO.GftTable):
        df_text = ls_pageid.as_mutable_column_tab()
        for item in df_text.iterrows():
            # logging.info(item)
            page = item[1]['Conclusion']
            try:
                text = preprocessing.preprocess_string(page)
            # ylog.debug(text)
            except:
                continue
            output.write(text.encode('utf-8'))
            output.write('\n'.encode('utf-8'))
    output.close()


def train_word2vec(gid):
    """
    extract page from gid, preprocessing text and train.

    Return:
    word2vec model
    """
    logging.basicConfig(
        format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)
    logging.info("start training")
    extract_pages(gid, gs_call)
    from tempfile import gettempdir
    tmp_dir = gettempdir()
    txt_path = tmp_dir + '/test.txt'
    model = gensim.models.Word2Vec(
        LineSentence(txt_path),
        size=200,
        window=5,
        min_count=2,
        workers=multiprocessing.cpu_count())
    return model.wv
