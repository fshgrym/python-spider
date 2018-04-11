# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime

from ..items import DaomuItemLoader,DaomuItem


class SpiderSpider(scrapy.Spider):
    name = 'daomu'
    allowed_domains = ['www.daomubiji.com']
    start_urls = ['http://www.daomubiji.com/dao-mu-bi-ji-{}'.format(i) for i in range(1,9)]

    def parse(self, response):
        article_links = response.xpath('//div[@class="excerpts"]//a/@href').extract()
        for url in article_links:
            yield scrapy.Request(url,callback=self.parse_detail)

    def parse_detail(self,response):
        item = DaomuItemLoader(item=DaomuItem(), response=response)
        item.add_css('title', '.article-title::text')
        item.add_xpath('category', '//div[@class="article-meta"]/span[2]/a/text()')
        item.add_xpath('create_time', '//div[@class="article-meta"]/span[1]/text()')
        item.add_xpath('text', '//article[@class="article-content"]')
        item.add_value('crawl_time', datetime.now())
        a=item.load_item()
        yield a


