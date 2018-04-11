# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from ..items import DingdianItemLoad,DingdianItem
from ..settings import SQL_DATA_FORMAT
from datetime import datetime
class DingdianSpider(CrawlSpider):
    name = 'Dingdian'
    allowed_domains = ['x23us.com']
    start_urls = ['https://www.x23us.com/']

    rules = (
        Rule(LinkExtractor(allow=r'class/.*.html'),follow=True),
        Rule(LinkExtractor(allow=r'quanben/\d+'),follow=True),
        Rule(LinkExtractor(allow=r'book/\d+'), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        # i = {}
        #i['domain_id'] = response.xpath('//input[@id="sid"]/@value').extract()
        #i['name'] = response.xpath('//div[@id="name"]').extract()
        #i['description'] = response.xpath('//div[@id="description"]').extract()
        item = DingdianItemLoad(item=DingdianItem(),response=response)
        item.add_xpath('article_type','//*[@id="at"]/tr[1]/td[1]/a/text()')
        item.add_value('article_id',response.url)
        item.add_xpath('title','//*[@id="content"]/dd[1]/h1/text()')
        item.add_xpath('fav_nums','//*[@id="at"]/tr[2]/td[1]/text()')
        item.add_xpath('total_click_nums','//*[@id="at"]/tr[3]/td[1]/text()')
        item.add_xpath('recommend_nums','//*[@id="at"]/tr[4]/td[1]/text()')
        item.add_xpath('author','//*[@id="at"]/tr[1]/td[2]/text()')
        item.add_xpath('article_len','//*[@id="at"]/tr[2]/td[2]/text()')
        item.add_xpath('month_click_nums','//*[@id="at"]/tr[3]/td[2]/text()')
        item.add_xpath('month_fav_nums','//*[@id="at"]/tr[4]/td[2]/text()')
        item.add_xpath('article_status','//*[@id="at"]/tr[1]/td[3]/text()')
        item.add_xpath('update_time','//*[@id="at"]/tr[2]/td[3]/text()')
        item.add_xpath('week_click_nums','//*[@id="at"]/tr[3]/td[3]/text()')
        item.add_xpath('week_fav_nums','//*[@id="at"]/tr[4]/td[3]/text()')
        item.add_value('crawl_time',datetime.now())
        i=item.load_item()
        return i