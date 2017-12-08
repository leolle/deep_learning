# -*- coding: utf-8 -*-
import numpy as np
from gensim.models import word2vec
from gensim.models import KeyedVectors
from gensim.models.phrases import Phrases, Phraser
import os
import itertools
import re
from nltk import tokenize as n_tokenize
from pattern.en import tokenize as p_tokenize
import pprint
text = '''
the mayor of new york was there.
machine learning can be useful sometimes.
The titular threat of The Blob has always struck me as the ultimate movie
monster.
an insatiably hungry, amoeba-like mass able to penetrate
virtually any safeguard, capable of--as a doomed doctor chillingly
describes it--"assimilating flesh on contact.
Snide comparisons to gelatin be damned.
it's a concept with the most
devastating of potential consequences.
not unlike the grey goo scenario
proposed by technological theorists fearful of
artificial intelligence run rampant.
Sentence boundary disambiguation (SBD), also known as sentence breaking.
is the problem in natural language processing of deciding where sentences begin and end.
Often natural language processing tools require their input to be divided into sentences for a number of reasons.
However sentence boundary identification is challenging because punctuation marks are often ambiguous.
For example, a period may denote an abbreviation, decimal point, an ellipsis, or an email address – not the end of a sentence.
About 47% of the periods in the Wall Street Journal corpus denote abbreviations.
As well, question marks and exclamation marks may appear in embedded quotations, emoticons, computer code, and slang. Languages like Japanese and Chinese have unambiguous sentence-ending markers.
Clinical informatics is concerned with the use of information in health care by and for clinicians.[16][17]
Clinical informaticians, also known as clinical informaticists, transform health care by analyzing, designing, implementing, and evaluating information and communication systems that enhance individual and population health outcomes, improve [patient] care, and strengthen the clinician-patient relationship. Clinical informaticians use their knowledge of patient care combined with their understanding of informatics concepts, methods, and health informatics tools to:
assess information and knowledge needs of health care professionals, patients and their families.
characterize, evaluate, and refine clinical processes,
develop, implement, and refine clinical decision support systems, and
lead or participate in the procurement, customization, development, implementation, management, evaluation, and continuous improvement of clinical information systems.
Clinicians collaborate with other health care and information technology professionals to develop health informatics tools which promote patient care that is safe, efficient, effective, timely, patient-centered, and equitable. Many clinical informaticists are also computer scientists.
In October 2011 American Board of Medical Specialties (ABMS), the organization overseeing the certification of specialist MDs in the United States, announced the creation of MD-only physician certification in clinical informatics. The first examination for board certification in the subspecialty of clinical informatics was offered in October 2013 by American Board of Preventive Medicine (ABPM) with 432 passing to become the 2014 inaugural class of Diplomates in clinical informatics.[18]
Fellowship programs exist for physicians who wish to become board-certified in clinical informatics. Physicians must have graduated from a medical school in the United States or Canada, or a school located elsewhere that is approved by the ABPM. In addition, they must complete a primary residency program such as Internal Medicine (or any of the 24 subspecialties recognized by the ABMS) and be eligible to become licensed to practice medicine in the state where their fellowship program is located.[19] The fellowship program is 24 months in length, with fellows dividing their time between Informatics rotations, didactics, research, and clinical work in their primary specialty.
Integrated data repository[edit]

Achilles tool for data characterization of a healthcare dataset
One of the fundamental elements of biomedical and translational research is the use of integrated data repositories. A survey conducted in 2010 defined "integrated data repository" (IDR) as a data warehouse incorporating various sources of clinical data to support queries for a range of research-like functions.[20] Integrated data repositories are complex systems developed to solve a variety of problems ranging from identity management, protection of confidentiality, semantic and syntactic comparability of data from different sources, and most importantly convenient and flexible query.[21] Development of the field of clinical informatics led to the creation of large data sets with electronic health record data integrated with other data (such as genomic data). Types of data repositories include operational data stores (ODSs), clinical data warehouses (CDWs), clinical data marts, and clinical registries.[22] Operational data stores established for extracting, transferring and loading before creating warehouse or data marts.[22] Clinical registries repositories have long been in existence, but their contents are disease specific and sometimes considered archaic.[22] Clinical data stores and clinical data warehouses are considered fast and reliable. Though these large integrated repositories have impacted clinical research significantly, it still faces challenges and barriers. One big problem is the requirement for ethical approval by the institutional review board (IRB) for each research analysis meant for publication.[23] Some research resources do not require IRB approval. For example, CDWs with data of deceased patients have been de-identified and IRB approval is not required for their usage.[23][20][22][21] However, privacy sensitive data may still be explored by researchers when shared through its metadata and services, for example by following a linked open data perspective.[24] Another challenge is data quality. Methods that adjust for bias (such as using propensity score matching methods) assume that a complete health record is captured. Tools that examine data quality (e.g., point to missing data) help in discovering data quality problems.
'''


def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, ' ', raw_html)
    return cleantext


# sentence_stream = [[
#     u'the', u'mayor', u'of', u'new', u'york', u'was', u'there'
# ], [u'machine', u'learning', u'can', u'be', u'useful', u'sometimes'],
#                    ['new', 'york', 'mayor', 'was', 'present']]
# phrases = Phrases(sentence_stream, min_count=1, threshold=2)
# bigram = Phraser(phrases)
# sent = [u'the', u'mayor', u'of', u'new', u'york', u'was', u'there']
# pprint.pprint(bigram[sent])
# print('\n')
# pprint.pprint(list(bigram[sentence_stream]))

import logging
logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

cur_dir = os.getcwd()
glove_path = '/home/weiwu/share'
name = 'computer_age_statis.pdf'
file_name = os.path.join(cur_dir + '/data/docs/', name)
txt_file = os.path.join(cur_dir, name)

sentences = word2vec.Text8Corpus('text8')
import nltk.data
tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
# print '\n-----\n'.join(tokenizer.tokenize(text))
words = []
sentences = n_tokenize.sent_tokenize(text)
for line in sentences:
    sline = line.strip()
    if sline == "":
        continue
    rline = cleanhtml(sline)
    tokenized_line = ' '.join(p_tokenize(rline))
    is_alpha_word_line = [
        word for word in tokenized_line.lower().split() if word.isalpha()
    ]
    words.append(is_alpha_word_line)

phrases = Phrases(words, min_count=1, threshold=2)
bigram = Phraser(phrases)
# sent = [u'the', u'mayor', u'of', u'new', u'york', u'was', u'there']
# pprint.pprint(bigram[sent])
print('\n')
# pprint.pprint(list(bigram[words]))

# model.most_similar(positive=['woman', 'king'], negative=['man'], topn=1)
# model.most_similar(positive=['woman', 'king'], negative=['man'], topn=2)
# model.most_similar(['titular'])
# model.save('text8.model')
# model.wv.save_word2vec_format('text.model.bin', binary=True)

# more_examples = ["he is she", "big bigger bad", "going went being"]
# for example in more_examples:
#     a, b, x = example.split()
#     predicted = model.most_similar([x, b], [a])[0][0]
#     print("'%s' is to '%s' as '%s' is to '%s'" % (a, b, x, predicted))
for _ in words:
    phrases = Phrases(_, min_count=1, threshold=2)
    print(phrases[_])
