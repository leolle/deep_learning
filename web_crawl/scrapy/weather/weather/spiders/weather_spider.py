# -*- coding: utf-8 -*-
import scrapy
from weather.items import WeatherItem


class WeatherSpider(scrapy.Spider):
    name = "weather"
    start_urls = [
        'http://weather.sina.com.cn/',
    ]
    allowed_domains = ['sina.com.cn']

    def parse(self, response):
        item = WeatherItem()
        item['city'] = response.xpath(
            'string(//*[@id="slider_ct_name"])').extract()
        # item['city'] = item['city'].encode('utf-8')
        print(item['city'][0].encode('utf-8'))
        ten_day = response.xpath('//*[@id="blk_fc_c0_scroll"]')
        item['date'] = ten_day.css('p.wt_fc_c0_i_date::text').extract()
        item['day_week'] = ten_day.css('p.wt_fc_c0_i_day::text').extract()
        item['day_desc'] = ten_day.css('img.icons0_wt::attr(title)').extract()
        item['day_temp'] = ten_day.css('p.wt_fc_c0_i_temp::text').extract()
        item['day_tip'] = ten_day.css('p.wt_fc_c0_i_tip::text').extract()

        return item
