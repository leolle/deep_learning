# -*- coding: utf-8 -*-
"""test snownlp methods, including training, sentiment classification, keywords, summarization"""
from snownlp import SnowNLP
# from snownlp.sentiment import Sentiment
from snownlp.sentiment import train, save
# sentiment = Sentiment()
# sentiment.load(
#     '/home/weiwu/.virtualenvs/graph/lib/python3.6/site-packages/snownlp/sentiment/sentiment.marshal'
# )
sent = u'这个东西一般'
# print(sentiment.classify(sent))
pos_docs = '/home/weiwu/.virtualenvs/graph/lib/python3.6/site-packages/snownlp/sentiment/pos.txt'
neg_docs = '/home/weiwu/.virtualenvs/graph/lib/python3.6/site-packages/snownlp/sentiment/neg.txt'
sentiment_model_path = './data/model/sentiment.marshal'

# sentiment.train(pos_docs=pos_docs, neg_docs=neg_docs)
# sentiment.save(sentiment_model_path)
# train(neg_docs, pos_docs)
# save(sentiment_model_path)
# next
# print('tokenization', s.words)  # [u'这个', u'东西', u'真心',
# #  u'很', u'赞']


# print('targs', s.tags)  # [(u'这个', u'r'), (u'东西', u'n'),
# #  (u'真心', u'd'), (u'很', u'd'),
# #  (u'赞', u'Vg')]
def sentiment_classification(text=u'这个东西一般'):
    s = SnowNLP(text)
    print('sentiment', s.sentiments)  # 0.9769663402895832 positive的概率


def pingying(text):
    s = SnowNLP(text)
    return s.pinyin  # [u'zhe', u'ge', u'dong', u'xi',
    #  u'zhen', u'xin', u'hen', u'zan']


def zht_to_zhs(zht=u'「繁體字」「繁體中文」的叫法在臺灣亦很常見。'):

    s = SnowNLP(zht)

    return s.han  # u'「繁体字」「繁体中文」的叫法
    # 在台湾亦很常见。'


text = u'''1、公司深度报告：寻价格涨跌之因、需求之形，论茅台的成长
2、核心观点：茅台价格作为白酒板块的风向标，受到消费需求、投资需求以及公司量价政策的共同影响。
3、在新一轮价格上行周期中，大众消费崛起和商务消费复苏推动消费需求回暖，增库存周期的启动造就“越涨越买”的循环，且公司积极运用量价政策进行市场调节，共同推动茅台价格持续上涨并趋于稳定，但市场对茅台开瓶率以及库存等相关问题依存隐忧。
4、本文重点分析了库存的形态、测算方法以及厂家应对的政策。
5、我们得出，2015年至今新增的茅台库存（显性+隐性库存）不足2个月，在厂家强有力的管控下，库存有望进一步降低。
6、考虑到涨价预期的存在，我们预计公司依旧处于需求周期和库存周期共振的通道中，量价有望持续超预期，建议积极布局。
7、茅台价格之谜：茅台价格不仅受到消费者的广泛关注，还是资本市场长期关注的焦点，经历上一轮周期的暴涨暴跌之后，目前正处于新一轮的上行周期。
8、我们选取最能反映行业景气度的一批价作为研究的价格指标，从消费需求、投资需求和供给等三个层面对茅台价格的影响因素和传导机制进行研究。
9、答案消费需求—大众消费崛起，商务消费复苏。
10、在新一轮成长周期中，大众消费和商务消费是茅台需求的主要贡献力量。
11、大众消费崛起一方面来自于中产阶级为代表的消费群体的扩大，另一方面受益于居民消费能力和消费意愿的提升。
12、商务消费复苏与固投、地产等宏观经济回暖密切相关，固投、地产催生的大量商业活动直接拉动高端白酒回暖，房价上涨带来的财富效应也导致居民对茅台的消费意愿增强。
13、答案投资需求—奇货可居，越涨越买。
14、茅台具有保质期长、相对稀缺、保值增值等金融属性，因此茅台价格还受到投资需求的影响。
15、当市场对茅台产生涨价预期时，加杠杆买货行为意味着增库存周期启动，随之带动需求强劲提升并推动价格上涨，并形成“越涨越买”的正向循环。
16、我们通过对比茅台和五粮液在本轮周期中的销量增速，发现茅台销量增长明显快于五粮液，认为这是由于现阶段五粮液主要体现消费需求，而缺席投资需求，基于此，我们推算出2017年茅台酒投资需求占比约21.7%。
17、答案供给因素—因价制宜，从量价配合感受经营的艺术。
18、客观上，茅台供应偏紧是价格上涨的内在推动力；
19、主观上，茅台根据不同价格阶段面临的关键矛盾，积极运用各种量价政策调节市场价格，具体可分为三个阶段：控量挺价阶段，主要对应2016年，此阶段关键矛盾是改善渠道盈利，茅台通过控制发货节奏、严惩违规经销商以及取消优惠等控量手段，成功实现价格逐步回升；
20、提价放量阶段，主要对应2018年，此阶段关键矛盾为平抑价格泡沫，为此茅台五年来首次提价并加大春节投放量，目前来看价格已实现阶段性稳定。
21、首先我们复盘上一轮周期，发现上轮价格崩盘主要源于消费结构不合理、渠道囤货现象严重以及不科学的量价政策，因此认为本轮周期不会重蹈上轮崩盘覆辙。
22、未来展望来看，供给端预计缓慢提升，需求端预计延续扩张，因此供需偏紧格局将长期存在。
23、结合厂家、监管层以及社会舆论对茅台价格的治理作用，我们认为茅台价格未来将保持稳中有升的上涨节奏。
24、我们基于人均收入对应的合理购买力水平，测算出2020年茅台的合理终端价区间为1536元~1920元。
25、投资建议：重申“买入”评级。
26、我们预计：需求端，随着消费升级红利延续且当前库存水位健康（20%），茅台将进入需求周期和库存周期的共振阶段；
27、供给端，公司供应偏紧持续存在，且定价权愈发收放自如，考虑到当前渠道价差充足，公司具备持续提价能力。
28、中长期来看，我们认为公司收入有望持续保持20%以上的稳健增长，建议以更长远视角来看待公司的良好投资机会。
29、我们预计公司2018-2020年营业总收入分别为801.75/973.17/1151.52亿元，同比增长31.3%/21.4%/18.3%；
30、净利润分别为373.61/461.58/550.10亿元，同比增长37.97%/23.55%/19.18%，对应EPS分别为29.74/36.74/43.79元。
31、风险提示：打压三公消费力度继续加大、高端酒动销不及预期、食品安全事件。'''
with open('./data/test.china_tax.txt') as f:
    article = f.read()

s = SnowNLP(article)

print('keywords', s.keywords(100))  # [u'语言', u'自然', u'计算机']

print('summary', s.summary(5))  # [u'因而它是计算机科学的一部分',
#  u'自然语言处理是一门融语言学、计算机科学、
#	 数学于一体的科学',
#  u'自然语言处理是计算机科学领域与人工智能
#	 领域中的一个重要方向']
# print('sentences', s.sentences)

# s = SnowNLP([[u'这篇', u'文章'], [u'那篇', u'论文'], [u'这个']])
# print(s.tf)
# print(s.idf)
# print(s.sim([u'文章']))  # [0.3756070762985226, 0, 0]
