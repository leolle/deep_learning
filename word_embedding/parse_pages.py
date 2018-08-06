# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
import pandas as pd
import numpy as np
pages_file_path = '/home/weiwu/share/deep_learning/data/zh_finance_pages_level_3.csv'
df_wiki_index = pd.read_csv(pages_file_path)
# sr_pages = df_pages.title.apply(lambda x: x.replace('_', " "))
