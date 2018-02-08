#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
"""
import logging
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
    convert skill_pb2.RespRunNodeAction to graphUpload.proto.Graph
    so that in python we have only one graph format.

    Keyword Arguments:
    resp_run_node_action -- skill_pb2.RespRunNodeAction, result from get_graph_from_neo4j

    Return:
    graphUpload_pb2.graph
    """
    graph_upload_request = graphUpload_pb2.GraphUploadRequest()

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
gftIO.test_skill_2_graph('D81A370D094AAAC4A018AFBE409A645A', gs_call)
# graph = gs_call.get_graph_from_neo4j('D81A370D094AAAC4A018AFBE409A645A')
# graph_message = graphUpload_pb2.Graph()
# # edges = graph.graphs[0].graph
# nodes = {}
# for n in graph.graphs[0].graph.nodes:
#     node = graph_message.nodes.add()
#     print(n.nid)
#     for p in n.node_prop.props.entries:
#         if p.key == '_type':
#             node.props.type = p.value
#         elif p.key == '_gid':
#             nodes[n.nid] = p.value
#         else:
#             field = node.props.props.entries.add()
#             field.key = p.key
#             field.value = p.value
# for e in graph.graphs[0].graph.edges:
#     edge = graph_message.edges.add()
#     edge.props.type = e.type
#     for p in e.edge_prop.props.entries:
#         if p.key == '_type':
#             edge.props.type = p.value
#     edge.startNodeID.gid = nodes[e.sn_id]
#     edge.endNodeID.gid = nodes[e.en_id]

# graph_from_skill = gs_call.skill_result_2_graph(graph)
