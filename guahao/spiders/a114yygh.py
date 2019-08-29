# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from ..items import GuahaoItem, GuahaoItemLoader


class A114yyghSpider(CrawlSpider):
    name = '114yygh'
    allowed_domains = ['www.114yygh.com']

    custom_settings = {
        'CITY': '北京',
        'ITEM_PIPELINES': {
            'guahao.pipelines.MongoPipeline': 300,
        }
    }

    # start_urls = ['http://www.114yygh.com/hp/1_0_3_0.htm']
    def start_requests(self):
        for i in range(1, 12):
            url = 'http://www.114yygh.com/hp/{}_0_3_0.htm'.format(i)
            yield scrapy.Request(url)

    rules = (
        Rule(LinkExtractor(restrict_xpaths=('//*[@id="yiyuan_content"]/div/dl/dd/p/a')),
             ),  # 提取三级医院链接
        Rule(LinkExtractor(restrict_xpaths=('//div[@class="kfyuks_left"]//a[contains(text(), "肾")]')),
             callback='parse_item'),  # 提取肾内科链接，并返回response
    )

    def parse_item(self, response):
        """
        解析具体字段, 用input_processor清洗数据i
        :param response:
        :return: item
        """
        l = GuahaoItemLoader(item=GuahaoItem(), response=response)
        # 2、搜集数据，指定保存的字段名和css路径，
        l.add_css('hospital', 'div.ksorder_box_top > p > strong::text')
        l.add_css('department', 'div.ksorder_box_top > p > strong::text')
        loader = l.nested_css('dl.ksorder_box_con_dl > dd')
        loader.add_css('address', 'dl:nth-child(1) > dd > p::text')
        loader.add_css('website', 'dl:nth-child(2) > dd > p >a::text')
        loader.add_css('phone', 'dl:nth-child(3) > dd > p::text')
        l.add_css('traffic', 'dl:nth-child(4) > dd > p::text')
        l.add_xpath('order_rule', '//div[@class="ksorder_cen_r"]/div/ul/li')
        # 2、添加已经确定的值到loader中
        l.add_value('link', response.url)
        l.add_value('city', self.custom_settings['CITY'])
        # 3、调用load_item方法取出最终的item对象并返回
        return l.load_item()
