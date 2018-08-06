# -*- coding: utf-8 -*-
"""
Created on Wed Jan 24 10:08:03 2018

@author: zhaohua
"""

import axiv  
mg=seleniumTest()
#keyword='bayesian network finance'
keyword='svm finance'
pages=5
data_all=mg.gain_data(keyword,pages)
