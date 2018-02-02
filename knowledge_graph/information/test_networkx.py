# -*- coding: utf-8 -*-
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib import RcParams
import matplotlib.font_manager as mfm

G = nx.Graph()

# G.add_node(1)
# G.add_nodes_from([2, 3])
# H = nx.path_graph(10)
# G.add_nodes_from(H)
# G.add_node(H)
# G.add_edge(1, 2)
# e = (2, 3)
# G.add_edge(*e)  # unpack edge tuple*
# G.add_edges_from([(1, 2), (1, 3)])
# G.add_edges_from([(1, 2), (1, 3)])
# G.add_node(1)
# G.add_edge(1, 2)
# G.add_node("spam")  # adds node "spam"
# G.add_nodes_from("spam")  # adds 4 nodes: 's', 'p', 'a', 'm'
# G.add_edge(3, 'm')
# G.number_of_nodes()

# print(G.number_of_edges())

# DG = nx.DiGraph()
# DG.add_weighted_edges_from([(1, 2, 0.5), (3, 1, 0.75)])
# DG.out_degree(1, weight='weight')

# DG.degree(1, weight='weight')

# print(list(DG.successors(1)))
# print(list(DG.neighbors(1)))
str_test = u"""云南铜业股份有限公司	公司名称	云南铜业股份有限公司
云南铜业股份有限公司	总部地点	中国云南
云南铜业股份有限公司	成立时间	1998年
云南铜业股份有限公司	经营范围	铜冶炼
东方证券	公司名称	东方证券
东方证券	前身	东方证券有限责任公司
东方证券	成立时间	1998年3月
东方证券	类型	<a>综合类证券公司</a>
中国神华煤制油化工有限公司	公司名称	中国神华煤制油化工有限公司
中国神华煤制油化工有限公司	成立时间	2003年6月
中国神华煤制油化工有限公司	经营范围	柴油
中国神华煤制油化工有限公司	经营范围	液化气
中国神华煤制油化工有限公司	经营范围	石脑油
"""
sample_str = [x.split() for x in str_test.splitlines()]

for node in sample_str:
    G.add_nodes_from([node[0], node[2]])
    G.add_edge(node[0], node[2], relation=node[1])
nx.write_gexf(G, 'demo.gexf')
# G[node[0]][node[2][node[1]] = node[1]
# G = nx.petersen_graph()
import matplotlib as mpl
# mpl.rcParams['font.sans-serif'] = ['SimSun']
# mpl.rcParams['font.serif'] = ['SimSun']

# font_name = "SimSun"
# RcParams['font.family'] = ['SimSun']
# plt.text(0.5, 0.5, s=u'测试')
# plt.show()

font_path = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"
prop = mfm.FontProperties(fname=font_path)
# plt.text(
#     0.5,
#     0.5,
#     s=u'测试',)
# plt.show()

plt.subplot(121)
nx.draw(G, with_labels=True, font_weight='bold', font_family='SimSun')
# plt.subplot(122)
# nx.draw_shell(
#     G, nlist=[range(5, 10), range(5)], with_labels=True, font_weight='bold')
# plt.show()
