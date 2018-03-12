# -*- coding: utf-8 -*-
"""
Created on Wed Jan 31 10:19:11 2018

@author:Minirose
"""
import os
import json
import random
from urllib.parse import urlencode
from bs4 import BeautifulSoup
from time import sleep
import time
import re
from math import ceil
import requests
from config import USER_AGENT, LOGGER
from urllib.parse import urlparse


class TwitterSearch():

    # __metaclass__ = ABCMeta

    def __init__(self, rate_delay=2, error_delay=5):
        """
        :param rate_delay: How long to pause between calls to Twitter
        :param error_delay: How long to pause when an error occurs
        """
        PROXIES = [{
            'http': 'http://127.0.0.1:1080',
            'https': 'http://127.0.0.1:1080'
        }]
        self.rate_delay = rate_delay
        self.error_delay = error_delay
        self.proxies = random.choice(PROXIES)


#        if proxies :pass
#        else :None

    def gain_data(self, query, nums):
        """
        ###return url
        Scrape items from twitter
        :param query:   Query to search Twitter with. Takes form of queries constructed with using Twitters
                        advanced search: https://twitter.com/search-advanced
        """
        url = self.construct_url(query)
        # print url
        #        continue_search = True
        max_tweet = None
        response = self.execute_search(url)
        tweet_info = []
        nums = int(ceil(nums / 20))
        num = 1

        while response is not None and response['items_html'] is not None and num <= nums:

            # print num
            tweets = self.parse_tweets(response['items_html'])
            tweet_info = tweet_info + tweets

            # If we have no tweets, then we can break the loop early
            if len(tweets) == 0:
                break

            # If we haven't set our min tweet yet, set it now
            if max_tweet is None:
                max_tweet = tweets[0]

            # continue_search = self.save_tweets(tweets)

            # Our max tweet is the last tweet in the list
            min_tweet = tweets[-1]

            if max_tweet['tweet_id'] is not min_tweet['tweet_id']:
                max_position = "TWEET-%s-%s" % (min_tweet['tweet_id'],
                                                max_tweet['tweet_id'])
                url = self.construct_url(query, max_position=max_position)
                # Sleep for our rate_delay
                sleep(self.rate_delay)
                response = self.execute_search(url)
            num = num + 1

        return tweet_info

    def execute_search(self, url, pause=2):
        """
        Executes a search to Twitter for the given URL
        :param url: URL to search twitter with
        :return: A JSON object with data from Twitter
        """
        headers = {'user-agent': self.get_random_user_agent()}
        try:
            requests.packages.urllib3.disable_warnings(
                requests.packages.urllib3.exceptions.InsecureRequestWarning)
            r = requests.get(
                url=url,
                proxies=self.proxies,
                headers=headers,
                allow_redirects=False,
                verify=False,
                timeout=30)
            LOGGER.info(url)
            time.sleep(pause)
            content = r.text
            dejson = json.loads(content)
            return dejson

        # If we get a ValueError exception due to a request timing out, we sleep for our error delay, then make
        # another attempt
        except ValueError as e:
            # print e.message
            # print "Sleeping for %i" % self.error_delay
            sleep(self.error_delay)
            return self.execute_search(url)

    # @staticmethod
    def parse_tweets(self, items_html):
        """
        Parses Tweets from the given HTML
        :param items_html: The HTML block with tweets
        :return: A JSON list of tweets
        """
        bsObj = BeautifulSoup(items_html, "lxml")
        tweets = []
        for li in bsObj.find_all("li", class_='js-stream-item'):

            #        #    print li['data-item-id']
            #            print '*'*100
            if 'data-item-id' not in li.attrs:
                continue

            tweet = {
                'tweet_id': li['data-item-id'],
                'text': None,
                'user_id': None,
                'user_screen_name': None,
                'user_name': None,
                'created_at': None,
                'retweets': 0,
                'favorites': 0,
                'url_link': None,
                'profile_url': None,
                'repliestweets': None
            }

            text_p = li.find("p", class_="tweet-text")
            #    print text_p
            if text_p is not None:
                tweet['text'] = text_p.get_text().encode('utf-8')
                # print text_p.get_text().encode('utf-8')

            user_details_div = li.find("div", class_="tweet")
            if user_details_div is not None:
                tweet['user_id'] = user_details_div['data-user-id']
                # print user_details_div['data-user-id']
                tweet['user_screen_name'] = user_details_div['data-screen-name']
                # print user_details_div['data-screen-name']
                tweet['user_name'] = user_details_div['data-name']
                # print user_details_div['data-name']
                base_url = 'https://twitter.com/{}/status/{}'
                tweet['url_link'] = base_url.format(
                    user_details_div['data-screen-name'], li['data-item-id'])
                # print tweet['url_link']
                base_url2 = 'https://twitter.com/{}'
                tweet['profile_url'] = base_url2.format(
                    user_details_div['data-screen-name'])
                # print tweet['profile_url']
        #

        # Tweet date
            date_span = li.find("span", class_="_timestamp")
            if date_span is not None:
                tweet['created_at'] = float(date_span['data-time-ms'])
                # print float(date_span['data-time-ms'])

            # Tweet Retweets
            retweet_span = li.select(
                "span.ProfileTweet-action--retweet > span.ProfileTweet-actionCount"
            )
            if retweet_span is not None and len(retweet_span) > 0:
                tweet['retweets'] = int(
                    retweet_span[0]['data-tweet-stat-count'])
                # print int(retweet_span[0]['data-tweet-stat-count'])

            # Tweet Favourites
            favorite_span = li.select(
                "span.ProfileTweet-action--favorite > span.ProfileTweet-actionCount"
            )
            #    print favorite_span
            if favorite_span is not None and len(retweet_span) > 0:
                tweet['favorites'] = int(
                    favorite_span[0]['data-tweet-stat-count'])
                # print int(favorite_span[0]['data-tweet-stat-count'])

            # replies Retweets
            replies_span = li.find_all(
                'span', class_='ProfileTweet-actionCountForAria')[0].text
            #    print replies_span
            pattern = re.compile(u'(\d+)')
            tweet['repliestweets'] = int(re.findall(pattern, replies_span)[0])
            # print tweet['repliestweets']

            # print '*' * 100

            tweets.append(tweet)
        return tweets

    # @staticmethod
    def construct_url(self, query, max_position=None):
        """
        For a given query, will construct a URL to search Twitter with
        :param query: The query term used to search twitter
        :param max_position: The max_position value to select the next pagination of tweets
        :return: A string URL
        """

        params = {
            # Type Param
            'f': 'tweets',
            # Query Param
            'q': query
        }

        # If our max_position param is not None, we add it to the parameters
        if max_position is not None:
            params['max_position'] = max_position

        url_tupple = ('https', 'twitter.com', '/i/search/timeline', '',
                      urlencode(params), '')
        return urlparse(url_tupple)

    def get_random_user_agent(self):
        """
        Get a random user agent string.
        :return: Random user agent string.
        """
        return random.choice(self.get_data('user_agents.txt', USER_AGENT))

    def get_data(self, filename, default=''):
        """
        Get data from a file
        :param filename: filename
        :param default: default value
        :return: data
        """
        root_folder = os.path.dirname(__file__)
        user_agents_file = os.path.join(
            os.path.join(root_folder, 'data'), filename)
        try:
            with open(user_agents_file) as fp:
                data = [_.strip() for _ in fp.readlines()]
        except:
            data = [default]
        return data


def main():
    m = TwitterSearch()
    data = m.gain_data(query='证券 2017 2016', nums=60)


if __name__ == '__main__':
    main()
