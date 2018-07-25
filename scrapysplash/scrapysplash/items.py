# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ScrapysplashItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

from scrapy import Field,Item
class ProductItem(Item):
    collection = 'products' # 定义区分名字
    image = Field()
    price = Field()
    deal = Field()
    title = Field()
    shop = Field()
    location = Field()