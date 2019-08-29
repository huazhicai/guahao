# -*- coding: utf-8 -*-
import scrapy

from ..items import GradeItem


class A114ghSpider(scrapy.Spider):
    name = '114gh'
    allowed_domains = ['www.114yygh.com']

    custom_settings = {
        'ITEM_PIPELINES': {
            'guahao.pipelines.GradePipeline': 300,
        }
    }

    # start_urls = ['http://www.114yygh.com/hp/1_0_3_0.htm']
    def start_requests(self):
        for i in range(1, 12):
            url = 'http://www.114yygh.com/hp/{}_0_3_0.htm?'.format(i)
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        item = GradeItem()
        for i in response.xpath('//*[@id="yiyuan_content"]/div'):
            item['hospital'] = i.xpath('./dl/dd/p/a/text()').get()
            item['grade'] = i.xpath('./dl/dd/p/span/text()').get()
            yield item
