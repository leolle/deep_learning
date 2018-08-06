# -*- coding: utf-8 -*-
"""
Created on Wed Jan 24 10:08:03 2018

@author: zhaohua
"""

# import huxiu
from huxiu import Huxiu

mg = Huxiu()
infos = mg.gain_data(query='股票 基金 2017', nums=30)
