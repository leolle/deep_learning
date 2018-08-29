# -*- coding: utf-8 -*-
"""calculate similarity using tfidf vector distance"""
from gensim import corpora, models, similarities
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from nltk.tokenize import word_tokenize
from gensim.matutils import cossim
import jieba

# gensim的模型model模块，可以对corpus进行进一步的处理，比如tf-idf模型，lsi模型，lda模型等
wordstest_model = ["我去玉龙雪山并且喜欢玉龙雪山玉龙雪山", "我在玉龙雪山并且喜欢玉龙雪山"]
test_model = [[word for word in jieba.cut(words)] for words in wordstest_model]
dictionary = corpora.Dictionary(test_model, prune_at=2000000)
# for key in dictionary.iterkeys():
#     print key,dictionary.get(key),dictionary.dfs[key]
corpus_model = [dictionary.doc2bow(test) for test in test_model]
# print(corpus_model)
# similarity of two vector
print(cossim(corpus_model[0], corpus_model[1]))
# gensim的模型model模块，可以对corpus进行进一步的处理，比如tf-idf模型，lsi模型，lda模型等
wordstest_model = ["我去玉龙雪山并且喜欢玉龙雪山玉龙雪山", "我在玉龙雪山并且喜欢玉龙雪山", "我在九寨沟"]
test_model = [[word for word in jieba.cut(words)] for words in wordstest_model]
dictionary = corpora.Dictionary(test_model, prune_at=2000000)
# for key in dictionary.iterkeys():
#     print key,dictionary.get(key),dictionary.dfs[key]
corpus_model = [dictionary.doc2bow(test) for test in test_model]
print(corpus_model)
# [[(0, 1), (1, 3), (2, 1), (3, 1), (4, 1)], [(0, 1), (1, 2), (3, 1), (4, 1), (5, 1)], [(0, 1), (5, 1), (6, 1)]]

# 目前只是生成了一个模型,并不是将对应的corpus转化后的结果,里面存储有各个单词的词频，文频等信息
tfidf_model = models.TfidfModel(corpus_model)
# 对语料生成tfidf
corpus_tfidf = tfidf_model[corpus_model]

#使用测试文本来测试模型，提取关键词,test_bow提供当前文本词频，tfidf_model提供idf计算
testword = "我在九寨沟"
test_bow = dictionary.doc2bow([word for word in jieba.cut(testword)])
test_tfidf = tfidf_model[test_bow]
print(test_tfidf)
# 词id,tfidf值
# [(4, 0.32718457421365993), (5, 0.32718457421365993), (6, 0.8865102981879297)]
testword_1 = "我去玉龙雪山并且喜欢玉龙雪山玉龙雪山"
test_bow_1 = dictionary.doc2bow([word for word in jieba.cut(testword_1)])
test_tfidf_1 = tfidf_model[test_bow_1]
print(test_tfidf_1)

# compute similarity with raw vector
cossim(corpus_model[0], corpus_model[2])

# compute similarity with tf-idf
cossim(test_tfidf, test_bow_1)

# 计算相似度
index = similarities.MatrixSimilarity(corpus_tfidf)  #把所有评论做成索引
sims = index[test_tfidf]  #利用索引计算每一条评论和商品描述之间的相似度
print(sims)
# [ 0.07639694  0.2473283   0.94496047]
"""calculate similarity with doc2vec"""
# data = [
#     "I love machine learning. Its awesome.", "I love coding in python",
#     "I love building chatbots", "they chat amagingly well"
# ]
# tagged_data = [
#     TaggedDocument(words=[word for word in jieba.cut(_d)], tags=[str(i)])
#     for i, _d in enumerate(data)
# ]
# # tagged_data = [
# #     TaggedDocument(words=word_tokenize(_d.lower()), tags=[str(i)])
# #     for i, _d in enumerate(data)
# # ]

# max_epochs = 100
# vec_size = 20
# alpha = 0.025

# model = Doc2Vec(
#     size=vec_size, alpha=alpha, min_alpha=0.00025, min_count=1, dm=1)

# model.build_vocab(tagged_data)

# for epoch in range(max_epochs):
#     print('iteration {0}'.format(epoch))
#     model.train(
#         tagged_data, total_examples=model.corpus_count, epochs=model.iter)
#     # decrease the learning rate
#     model.alpha -= 0.0002
#     # fix the learning rate, no decay
#     model.min_alpha = model.alpha

# # test_data = word_tokenize("I love chatbots".lower())
# test_data = [word for word in jieba.cut('我在九寨沟,很喜欢')]
# v1 = model.infer_vector(test_data)
# print("V1_infer", v1)

# # to find most similar doc using tags
# similar_doc = model.docvecs.most_similar('0')
# print(similar_doc)

# # to find vector of doc in training data using tags or in other words, printing the vector of document at index 1 in training data
# print(model.docvecs['1'])
"""doc tfidf"""
input_text = """中国政府高层显然也希望避免中美冲突恶化, 中美贸易战开打, 但中美贸易战开打之后, 强调中国在贸易战中有"五大优势", 他强调："我们要特别防止中美之间的贸易冲突扩散到意识形态领域"""
test_model = [[word for word in jieba.cut(words)]
              for words in input_text.split()]
dictionary = corpora.Dictionary(test_model, prune_at=2000000)
# for key in dictionary.iterkeys():
#     print key,dictionary.get(key),dictionary.dfs[key]
corpus_model = [dictionary.doc2bow(test) for test in test_model]
print(corpus_model)
# [[(0, 1), (1, 3), (2, 1), (3, 1), (4, 1)], [(0, 1), (1, 2), (3, 1), (4, 1), (5, 1)], [(0, 1), (5, 1), (6, 1)]]

# 目前只是生成了一个模型,并不是将对应的corpus转化后的结果,里面存储有各个单词的词频，文频等信息
tfidf_model = models.TfidfModel(corpus_model)
# 对语料生成tfidf
corpus_tfidf = tfidf_model[corpus_model]
d = {dictionary.get(id): value for doc in corpus_tfidf for id, value in doc}
# 对tfidf排序
from operator import itemgetter
order = sorted(d.items(), key=itemgetter(1), reverse=True)
"""tfidf english sentences"""
input_text_translations = """The Chinese government’s top management obviously also hopes to avoid the deterioration of the Sino-US conflict. The Sino-US trade war has started. After the Sino-US trade war began, it emphasized that China has "five advantages" in the trade war. He stressed: "We must especially prevent Sino-US cooperation. Trade conflict spreads to the ideological field"""
from gensim import corpora, models, similarities
from nltk.tokenize import word_tokenize, sent_tokenize

test_model = word_tokenize(input_text_translations.lower())
wordstest_model = sent_tokenize(input_text_translations)
test_model = [word_tokenize(_d.lower()) for _d in docs]
# test_model = [[word for word in jieba.cut(words)] for words in wordstest_model]
dictionary = corpora.Dictionary(test_model, prune_at=2000000)
# for key in dictionary.iterkeys():
#     print key,dictionary.get(key),dictionary.dfs[key]
corpus_model = [dictionary.doc2bow(test) for test in test_model]
tfidf_model = models.TfidfModel(corpus_model)
# 对语料生成tfidf
corpus_tfidf = tfidf_model[corpus_model]
d = {}
d = {dictionary.get(id): value for doc in corpus_tfidf for id, value in doc}
from operator import itemgetter
sorted(d.items(), key=itemgetter(1), reverse=True)
