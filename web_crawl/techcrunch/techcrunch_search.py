# -*- coding: utf-8 -*-
"""
Created on Wed Jan 24 10:08:03 2018

@author: zhaohua
"""
# import techcrunch
from techcrunch import Techcrunch

mg = Techcrunch()
infos = mg.gain_data(query='证券 2017 2016', nums=60)
