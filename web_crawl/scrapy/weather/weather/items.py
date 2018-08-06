# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class WeatherItem(scrapy.Item):
    # define the fields for your item here like:
    city = scrapy.Field()
    date = scrapy.Field()
    day_desc = scrapy.Field()
    day_temp = scrapy.Field()
    day_tip = scrapy.Field()
    day_week = scrapy.Field()
