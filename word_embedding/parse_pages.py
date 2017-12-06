# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
import pandas as pd
import numpy as np
pages_file_path = '/home/weiwu/share/deep_learning/data/finance_pages_level_5.csv'
df_pages = pd.read_csv(pages_file_path)
sr_pages = df_pages.title.apply(lambda x: x.replace('_', " "))
