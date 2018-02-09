# -*- coding: utf-8 -*-

# Python program to detect cycle
# in a graph

from ylib import ylog
import re
import os
import sys
import logging
from tqdm import tqdm
import networkx as nx

ylog.set_level(logging.DEBUG)
ylog.console_on()

user_path = os.path.expanduser("~")
try:
    category_link_path = sys.argv[1]
except:
    category_link_path = user_path + \
        '/share/deep_learning/data/zhwiki_cat_pg_lk/zhwiki-latest-categorylinks.sql'
else:
    category_link_path = user_path + \
        '/share/deep_learning/data/zhwiki_cat_pg_lk/zhwiki-latest-categorylinks.sql'
# category_link_path = './data/zhwiki-latest-categorylinks.zhs.sql'
wiki_category_link_re = re.compile(
    "\(([0-9]+),('[^,]+'),('[^']+'),('\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'),('[^']*'),('[^,]+'),('[^,]+')\)"
)
graph = nx.DiGraph()


def upload_edge(dict_re_match_object):
    """ upload edge created from regular expression matched object.
    (9,'En-3_使用者','MOUNTAIN','2015-09-02 13:44:06','','uppercase','page')
    Keyword Arguments:
    re_match_object -- re object
    """
    # iterate nodes batch
    for index, value in dict_re_match_object.items():
        if value is not None:
            item = dict_re_match_object.get(index)
            edge_type = item.group(7)[1:-1]
            if edge_type == 'page':
                page_title = item.group(3)[1:-1]
                cat_title = item.group(2)[1:-1]
                if '\\n' in cat_title:
                    end = cat_title.split("\\n")
                    cat_title = end[-1]
                if '\\n' in page_title:
                    end = page_title.split("\\n")
                    page_title = end[-1]
                page_title = page_title.replace(" ", "_")
                # ylog.debug(cat_title)
                # ylog.debug(subcat_title)
                # if cat_title in EXAMPLE_CATEGORIES:
                graph.add_edge(cat_title, page_title, subtype='page')
            if edge_type == 'subcat':
                subcat_title = item.group(3)[1:-1]
                cat_title = item.group(2)[1:-1]
                if '\\n' in cat_title:
                    end = cat_title.split("\\n")
                    cat_title = end[-1]
                if '\\n' in subcat_title:
                    end = subcat_title.split("\\n")
                    subcat_title = end[-1]
                subcat_title = subcat_title.replace(" ", "_")
                # ylog.debug(cat_title)
                # ylog.debug(subcat_title)
                if subcat_title == cat_title:
                    continue
                graph.add_edge(cat_title, subcat_title, subtype='subcat')


#                g.addEdge(cat_title, subcat_title)
# if cat_title in EXAMPLE_CATEGORIES:


def batch_upload(re, file_path, batch_size, func, start, end):
    """batch upload categories or page
    Keyword Arguments:
    re         -- regular expression
    source     -- file path
    batch_size --
    func       -- upload function
    start      -- start position
    end        -- end position

    """
    # with open(file_path, 'r') as f:
    #     print("reading all lines from sql")
    #     total_line_size = len(f.readlines())
    with open(file_path, 'rb') as f:
        for i, line in enumerate(tqdm(f)):
            #         print("line #: %s/%s" % (i, 1503))
            #         print(len(line))
            # print(g.graph.keys())
            # print("line #: %s/%s" % (i, 1503))
            try:
                if i < start:
                    continue
                if i <= end:
                    line = line.decode('utf-8')
                    try:
                        last_span = re.search(line).span()[0]
                    except AttributeError:
                        continue
                    line_size = len(re.findall(line))
                    # ylog.debug(line_size)
                    for i in range(0, line_size, batch_size):
                        # pause if find a file naed pause at the currend dir
                        re_batch = {}
                        for j in range(batch_size):
                            re_batch[j] = re.search(line, last_span)
                            if re_batch[j] is not None:
                                last_span = re_batch[j].span()[1]
                        func(re_batch)
                else:
                    break
            except UnicodeDecodeError as e:
                last_span = e.start + 10
                line_size = len(re.findall(line))
                ylog.debug(line_size)
                for i in range(0, line_size, batch_size):
                    # pause if find a file naed pause at the currend dir
                    re_batch = {}
                    for j in range(batch_size):
                        re_batch[j] = re.search(line, last_span)
                        if re_batch[j] is not None:
                            last_span = re_batch[j].span()[1]
                    func(re_batch)

    # print(g.graph.keys())


batch_upload(
    wiki_category_link_re,
    category_link_path,
    200,
    upload_edge,
    start=0,
    end=10000)
# graph = nx.read_gexf('whole_edge.gexf')
nx.write_gexf(graph, 'whole_edges.gexf')
ls_nodes = list(graph.nodes)
counter = 0
total_nodes_num = 287966
rm_counter = 0
try:
    while True:
        ylog.debug('rm cycles loops number %s' % counter)

        for node in tqdm(ls_nodes):
            removed_counter = 0
            ylog.debug('rm cycles of node %s' % node)

            while True:
                try:
                    ls_loop = nx.find_cycle(graph, node)
                    # remove direct edge:
                    ylog.debug(ls_loop)
                    if len(ls_loop) == 2:
                        if ls_loop[0][0] == ls_loop[1][1] and ls_loop[0][1] == ls_loop[1][0]:
                            graph.remove_edge(ls_loop[0][0], ls_loop[0][1])
                    # remove big loop:
                    elif len(ls_loop) > 2:
                        graph.remove_edge(ls_loop[-1][0], ls_loop[-1][1])
                        # remove all edges in the loop, then next create edge first in.
                        # for i in range(len(ls_loop) - 1):
                        #     graph.remove_edge(ls_loop[i + 1][0],
                        #                       ls_loop[i + 1][1])
                    # counter = 0
                    removed_counter += 1
                except nx.NetworkXNoCycle:
                    counter += 1
                    if removed_counter != 0:
                        ylog.debug('rm cycles number %s' % removed_counter)
                    break

        if counter >= total_nodes_num - 1:
            break
except KeyboardInterrupt:
    nx.write_gexf(graph, 'whole_edges.no_loops.gexf')
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)
nx.write_gexf(graph, 'whole_edges.no_loops.gexf')
