#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
"""
import logging
import os
import re
import sys
from time import time, sleep
from timeit import default_timer
from tqdm import tqdm
from ylib import ylog
from lib.gftTools import gftIO
from lib.gftTools.proto import graphUpload_pb2
from lib.gftTools.gftIO import GSError

ylog.set_level(logging.DEBUG)
ylog.console_on()
# ylog.filelog_on("wiki_upload")
ylog.info("start")


def skill_result_2_graph(resp_run_node_action):
    """
    convert skill_pb2.RespRunNodeAction to graphUpload.proto.GraphUploadRequest.Graph
    so that in python we have only one graph format.


    Keyword Arguments:
    resp_run_node_action -- skill_pb2.RespRunNodeAction, result from get_graph_from_neo4j

    Return:
    graphUpload_pb2.graph
    """
    graph_upload_request = graphUpload_pb2.GraphUploadRequest()
    graph_upload_request.nodeAction4Duplication = graphUpload_pb2.Action4Duplication.Value(
        'UPDATE')
    graph_upload_request.edgeAction4Duplication = graphUpload_pb2.Action4Duplication.Value(
        'UPDATE')

    for n in resp_run_node_action.graphs[0].graph.nodes:
        node = graph_upload_request.graph.nodes.add()
        for p in n.node_prop.props.entries:
            if p.key == '_type':
                node.props.type = p.value
            elif p.key == '_s_graph_upload_tag':
                graph_upload_request.uploadTag = p.value
            else:
                field = node.props.props.entries.add()
                field.key = p.key
                field.value = p.value


# test fetch graph
test_url = 'http://192.168.1.166:9080'
# prod_url = 'http://q.gftchina.com:13567/vqservice/vq/'
test_user_name = 'wuwei'
test_pwd = 'gft'
gs_call = gftIO.GSCall(test_url, test_user_name, test_pwd)

graph = gs_call.get_graph_from_neo4j('D81A370D094AAAC4A018AFBE409A645A')
graph_upload_request = graphUpload_pb2.GraphUploadRequest()
# n = graph.graphs[0].graph.nodes[0]
# node = graph_upload_request.graph.nodes.add()
# for p in n.node_prop.props.entries:
#     if p.key == '_type':
#         node.props.type = p.value
#     elif p.key == '_s_graph_upload_tag':
#         graph_upload_request.uploadTag = p.value
#     else:
#         field = node.props.props.entries.add()
#         field.key = p.key
#         field.value = p.value
graph_upload_request.nodeAction4Duplication = graphUpload_pb2.Action4Duplication.Value(
    'UPDATE')
graph_upload_request.edgeAction4Duplication = graphUpload_pb2.Action4Duplication.Value(
    'UPDATE')

for n in graph.graphs[0].graph.nodes:
    node = graph_upload_request.graph.nodes.add()
    for p in n.node_prop.props.entries:
        if p.key == '_type':
            node.props.type = p.value
        elif p.key == '_s_graph_upload_tag':
            graph_upload_request.uploadTag = p.value
        else:
            field = node.props.props.entries.add()
            field.key = p.key
            field.value = p.value
