# -*- coding: utf-8 -*-
from scrapy import Item, Field
from scrapy.loader.processors import TakeFirst, MapCompose, Join, Identity
from scrapy.loader import ItemLoader
from w3lib.html import remove_tags


class GuahaoItem(Item):
    # define the fields for your item here like:
    collection = table = 'departments'
    hospital = Field(
        # 对传入到item的值调用指定的函数进行预处理，且自动传入当前字段值
        input_processor=MapCompose(lambda x: x.split('—')[0])
    )
    department = Field(
        input_processor=MapCompose(lambda x: x.split('—')[1])
    )
    address = Field()
    website = Field(
        input_processor=MapCompose(lambda x: x.strip().strip('http://'))
    )
    phone = Field()
    traffic = Field(
        input_processor=MapCompose(lambda x: x.strip())
    )
    order_rule = Field(
        input_processor=MapCompose(remove_tags, lambda x: x.split('\n')[0]),
        output_processor=Identity()
    )
    link = Field(
        input_processor=MapCompose(lambda x: x.strip())
    )
    city = Field()


class GuahaoItemLoader(ItemLoader):
    """自定制ItemLoader，取值都会调用TakeFirst函数"""
    default_output_processor = TakeFirst()


# ============================================== #
# a114gh 项目
class GradeItem(Item):
    collection = 'departments'
    hospital = Field()
    grade = Field()
