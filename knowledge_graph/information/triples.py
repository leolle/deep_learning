# -*- coding: utf-8 -*-
import pandas as pd

triples_file_path = '/home/weiwu/projects/deep_learning/knowledge_graph/database/company_triples.txt'
pd_triples = pd.read_csv(
    triples_file_path,
    header=None,
    delimiter='\t',
    names=['entity1', 'relation', 'entity2'])
relation = pd_triples['relation'].unique()
