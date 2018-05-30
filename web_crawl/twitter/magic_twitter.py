# -*- coding: utf-8 -*-
# from __future__ import unicode_literals
import json
import twitter

import logging
from deep_learning.web_crawl.config import LOGGER
from ylib import ylog
from ylib.yaml_config import Configuraion

ylog.set_level(logging.DEBUG)
ylog.console_on()
ylog.filelog_on("app")

logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)
config = Configuraion()

config.load('../config.yaml')
USER_AGENT = config.USER_AGENT
DOMAIN = config.DOMAIN
BLACK_DOMAIN = config.BLACK_DOMAIN
URL_SEARCH = config.URL_GOOGLE_SCHOLAR
PROXIES = config.PROXIES
rate_delay = 2
error_delay = 5

consumer_key = config.consumer_key
consumer_secret = config.consumer_secret
access_token = config.access_token
access_token_secret = config.access_token_secret

api = twitter.Api(
    consumer_key=consumer_key,
    consumer_secret=consumer_secret,
    access_token_key=access_token,
    access_token_secret=access_token_secret,
    proxies=PROXIES)
# Users to watch for should be a list. This will be joined by Twitter and the
# data returned will be for any tweet mentioning:
# @twitter *OR* @twitterapi *OR* @support.
USERS = [
    '@OpenAI', '@DeepMindAI', '@ubereng', '@MSFTResearch', '@ibmresearch',
    '@GoogleAI', '@berkeley_ai', '@MIT_CSAIL', '@MPI_IS', '@fhuszar',
    '@seb_ruder'
]

# Languages to filter tweets by is a list. This will be joined by Twitter
# to return data mentioning tweets only in the english language.
LANGUAGES = ['en']

# with open('output.txt', 'a') as f:
#     # api.GetStreamFilter will return a generator that yields one status
#     # message (i.e., Tweet) at a time as a JSON dictionary.
#     for line in api.GetStreamFilter(track=USERS, languages=LANGUAGES):
#         LOGGER.debug(line)
#         # f.write(json.dumps(line))
#         # f.write('\n')
users = api.GetFriends()
user_id = {}
print([u.screen_name for u in users])
for u in users:
    user_id[u.screen_name] = u.id
# for line in api.GetStreamFilter(track=USERS, languages=LANGUAGES):
# ylog.debug(line)
# To fetch a single user's public status messages, where "user" is either
# a Twitter "short name" or their user id.

# {{{
statuses = api.GetUserTimeline(user_id[USERS[0][1:]])
print([s.text for s in statuses])
