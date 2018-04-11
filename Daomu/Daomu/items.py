# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
from datetime import datetime
import scrapy
import re
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst,Join,MapCompose


class DaomuItemLoader(ItemLoader):
    default_output_processor = TakeFirst()#

# def date_convert(value):
#     data = datetime.strptime(value,'%Y-%m-%d %H:%M:%S')
def get_text(value):
    p = re.findall('<p>(.*?)</p>',value,re.S)
    return p


class DaomuItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    text = scrapy.Field(
        input_processor = MapCompose(get_text),#预处理
        output_processor = Join('\n')#把处理过的段落进行连接

    )
    create_time = scrapy.Field()
    category = scrapy.Field()
    crawl_time = scrapy.Field()



