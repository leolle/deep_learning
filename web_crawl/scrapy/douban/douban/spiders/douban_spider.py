# -*- coding: utf-8 -*-
import scrapy
from douban.items import DoubanItem
import re


class DoubanSpider(scrapy.Spider):
    name = "douban"
    start_urls = [
        'https://www.douban.com/doulist/1264675/',
    ]
    allowed_domains = ['douban.com']

    def parse(self, response):
        item = DoubanItem()
        books = response.xpath('//div[@class="bd doulist-subject"]')
        for book in books:
            title = book.xpath('div[@class="title"]/a/text()').extract()[0]
            rate = book.xpath(
                'div[@class="rating"]/span[@class="rating_nums"]/text()'
            ).extract()[0]
            author = re.search('<div class="abstract">(.*?)<br',
                               book.extract(), re.S).group(1)
            item['title'] = title.replace(" ", "").replace("\n", "")
            item['author'] = author.replace(" ", "").replace("\n", "")
            item['rate'] = rate
            yield item
            nextPage = response.xpath(
                '//span[@class="next"]/link/@href').extract()
            if nextPage:
                next = nextPage[0]
                print(next)
                yield scrapy.http.Request(next, callback=self.parse)
