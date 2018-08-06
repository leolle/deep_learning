# -*- coding: utf-8 -*-
"""
Automated tests for the parsing module.
"""

import logging
import unittest
import numpy as np
from preprocessing import remove_stopwords, strip_numeric, strip_punctuation2,\
    cut_article, cut_paragraph

# several documents
doc1 = u"""人口密度

人口密度是指在一定时期一定单位面积土地上的平均人口数目，计算方式是其总人口数除以总面积。一般使用的单位是每平方公里人数或每平方米所居住的人口数。
人口密度是反映人口分布疏密程度的常用数量指标。它通常用于计算一个国家、地区、城市或全球的人口分布状况。
适当的人口密度能够保证良好的居住、卫生及经济条件。
以下为世界人口密度最高的10个国家或地区：
以下为世界人口密度最低的10个国家或地区："""

doc2 = u"""原子核
极小，它的直径在10-15m~10-14m之间，体积只占原子体积的几千亿分之一，在这极小的原子核里却集中了99.96%以上原子的质量。原子核的密度极大，核密度约为1017kg/m3，即1m3的体积如装满原子核，其质量将达到1014t，即1百万亿吨。原子核的能量极大。构成原子核的质子和中子之间存在着巨大的吸引力，能克服质子之间所带正电荷的斥力而结合成原子核，使原子在化学反应中原子核不发生分裂。当一些原子核发生裂变（原子核分裂为两个或更多的核）或聚变（轻原子核相遇时结合成为重核）时，会释放出巨大的原子核能，即原子能（例如核能发电）。利用这一性质，方便人们的生活。整个原子不显电性是中性。"""

doc3 = u"""人口密度
人口密度是指在一定时期一定单位面积土地上的平均人口数目，计算方式是其总人口数除以总面积。一般使用的单位是每平方公里人数或每平方米所居住的人口数。人口密度是反映人口分布疏密程度的常用数量指标。它通常用于计算一个国家、地区、城市或全球的人口分布状况。适当的人口密度能够保证良好的居住、卫生及经济条件。
以下为世界人口密度最高的10个国家或地区：
以下为世界人口密度最低的10个国家或地区："""

doc4 = u"""人口密度人口密度是指在一定时期一定单位面积土地上的平均人口数目，计算方式是其总人口数除以总面积。一般使用的单位是每平方公里人数或每平方米所居住的人口数。人口密度是反映人口分布疏密程度的常用数量指标。它通常用于计算一个国家、地区、城市或全球的人口分布状况。适当的人口密度能够保证良好的居住、卫生及经济条件。以下为世界人口密度最高的10个国家或地区：以下为世界人口密度最低的10个国家或地区："""

doc5 = u"""人口密度

人口密度是指在一定时期一定单位面积土地上的平均人口数目，计算方式是其总人口数除以总面积。一般使用的单位是每平方公里人数或每平方米所居住的人口数。

人口密度是反映人口分布疏密程度的常用数量指标。它通常用于计算一个国家、地区、城市或全球的人口分布状况。

适当的人口密度能够保证良好的居住、卫生及经济条件。



以下为世界人口密度最高的10个国家或地区：
以下为世界人口密度最低的10个国家或地区：
"""

dataset = [strip_punctuation2(x.lower()) for x in [doc1, doc2, doc3, doc4]]
# doc1 and doc2 have class 0, doc3 and doc4 avec class 1
classes = np.array([[1, 0], [1, 0], [0, 1], [0, 1]])


class TestPreprocessing(unittest.TestCase):

    def testStripNumeric(self):
        self.assertEqual(
            strip_numeric("salut les amis du 59"), "salut les amis du ")

    def testStripPunctuation(self):
        self.assertEqual(strip_punctuation2(u"国家、地区."), u"国家 地区 ")

    def testStripStopwords(self):
        self.assertEqual(
            remove_stopwords("the world is square"), " world  square")
        self.assertEqual(
            remove_stopwords(u"一般使用的单位是人数或居住的人口数。"), u"使用单位人数居住人口数。")

    # def testCut(self):
    #     self.assertEqual(cut_paragraph(doc5), doc3)
    #     self.assertEqual(cut_article(doc5), doc4)


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    unittest.main()
