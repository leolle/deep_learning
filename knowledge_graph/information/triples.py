# -*- coding: utf-8 -*-
import pandas as pd

triples_file_path = '/home/weiwu/share/deep_learning/data/zhwiki/baike_triples.txt'
pd_triples = pd.read_csv(
    triples_file_path,
    header=None,
    delimiter='\t',
    names=['entity1', 'relation', 'entity2'])
