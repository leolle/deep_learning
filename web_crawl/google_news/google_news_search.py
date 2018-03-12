# -*- coding: utf-8 -*-
"""
Created on Wed Jan 24 10:34:53 2018

@author: Administrator
"""

import os
import sys
import time
import random
import pprint
import MagicGoogle_News
from MagicGoogle_News import MagicGoogle_News

PROXIES = [{
    'http': 'http://127.0.0.1:1080',
    'https': 'http://127.0.0.1:1080'
}]


mg = MagicGoogle_News(PROXIES)
m=mg.all_data(keywords='安徽 芜湖 无为',language='en',num=100)
time.sleep(random.randint(1, 5))



















###进行测试检查###
https://www.google.com/search?hl='en'&q='茅台'&btnG=Search&gbv=2&source=lnms&tbm=nws
https://www.google.com/search?hl='en'&q='茅台'&btnG=Search&gbv=1&num=100
https://www.google.com/search?hl='en'&q='茅台'&btnG=Search&gbv=1&num=100&start=20

###search 函数可以
for i in mg.search(query='茅台', language='en'):
    pprint.pprint(i)
m=mg.search(query='茅台', language='en')
time.sleep(random.randint(1, 5))

#######counts_result可以
result = mg.counts_result(query='茅台', language='en',num=20)
print(result)
time.sleep(random.randint(1, 5))


##############req_url##可以
result = mg.req_url(query='茅台',language='en',num=20)
print(result)



######search_page###可以
result = mg.search_page(query='茅台', num=20, language='en')
print(result)
time.sleep(random.randint(1, 5))





# ##search_url
for i in mg.search_url(query='茅台',language='en'):
    pprint.pprint(i)
time.sleep(random.randint(1, 5))


#####filter_link可以
#########pq_html可以

######get_random_user_agent
#########get_random_domain可以
#########get_data可以


m=mg.search_news(query='茅台',language='en')
time.sleep(random.randint(1, 5))


m=mg.all_data(query='茅台',language='en')
time.sleep(random.randint(1, 5))


search_relation
result = mg.search_relation(query='茅台', num=20, language='en')
for url in mg.search_relation(query='薛之谦'):
    pprint.pprint(url)





https://www.google.com/search?hl='en'&q='茅台'&btnG=Search&gbv=1&num=100
for i in mg.search(query='茅台', language='en',num=20):
    pprint.pprint(i)
m=mg.search(query='茅台', language='en')
time.sleep(random.randint(1, 5))

#######counts_result可以
result = mg.counts_result(query='茅台', language='en',num=20)
print(result)
time.sleep(random.randint(1, 5))


##############req_url##可以
result = mg.req_url(query='茅台',language='en',num=20)
print(result)


######search_page###可以
result = mg.search_page(query='茅台', num=20, language='en',num=20)
print(result)
time.sleep(random.randint(1, 5))





# ##search_url
for i in mg.search_url(query='茅台',language='en',num=20):
    pprint.pprint(i)
time.sleep(random.randint(1, 5))


#####filter_link可以
#########pq_html可以

######get_random_user_agent
#########get_random_domain可以
#########get_data可以



m=mg.all_data(query='茅台',language='en',num=20)
time.sleep(random.randint(1, 5))







https://www.google.com/search?hl='en'&q='茅台'&btnG=Search&gbv=1&num=100&start=20

for i in mg.search(query='茅台', language='en',num=20,start=20):
    pprint.pprint(i)
m=mg.search(query='茅台', language='en')
time.sleep(random.randint(1, 5))

#######counts_result可以
result = mg.counts_result(query='茅台', language='en',num=20,start=20)
print(result)
time.sleep(random.randint(1, 5))


##############req_url##可以
result = mg.req_url(query='茅台',language='en',num=20,start=20)
print(result)



######search_page###可以
result = mg.search_page(query='茅台', num=20, language='en',num=20)
print(result)
time.sleep(random.randint(1, 5))





# ##search_url
for i in mg.search_url(query='茅台',language='en',num=20):
    pprint.pprint(i)
time.sleep(random.randint(1, 5))


#####filter_link可以
#########pq_html可以

######get_random_user_agent
#########get_random_domain可以
#########get_data可以



m=mg.all_data(query='茅台',language='en',num=20)
time.sleep(random.randint(1, 5))

print type(m)

import  json
dict_to_json=json.dumps(m)
json_to_dict=json.loads(dict_to_json)
