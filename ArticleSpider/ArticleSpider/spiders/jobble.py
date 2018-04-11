# -*- coding: utf-8 -*-
import scrapy
import re
import datetime
from scrapy.loader import ItemLoader
from scrapy.http import  Request
from urllib import parse
from ArticleSpider.items import JobBoleArticleItem,ArticleSpiderItem
from ArticleSpider.utils.common import get_md5
from selenium import webdriver

from scrapy.xlib.pydispatch import dispatcher #信号分发器
from scrapy import signals #信号

class JobbleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/hbhb']

    # def __init__(self):
    #     self.browser = webdriver.Chrome()
    #     super(JobbleSpider,self).__init__()
    #     dispatcher.connect(self.spider_closed,signals.spider_closed)
    #
    # def spider_closed(self,spider):
    #     #当爬虫关闭的时候关闭浏览器
    #     print('spider closed')
    #     self.browser.quit()

    # 收集jobbole所有404的url和多少个页面
    handle_httpstatus_list = [404]

    def __init__(self):
        self.fail_urls = []
        dispatcher.connect(self.handles_spider_close, signals.spider_closed)

    def handles_spider_close(self,spider,reason):
        self.crawler.stats.set_value('failed_urls',','.join(self.fail_urls))



    def parse(self, response):
        '''
        1.提取所有文章的链接
        2.返回下一页
        :param response:
        :return:
        '''
        if response.status == 404:
            self.fail_urls.append(response.url)#数据收集器
            self.crawler.stats.inc_value('failed_url')#如果404就添加到crawler.stats.inc_value

        post_nodes= response.css('#archive div.floated-thumb div.post-thumb a')
        for post_node in post_nodes:
            image = post_node.css('img::attr(src)').extract_first()
            post_url = post_node.css('::attr(href)').extract_first()
            yield Request(url=parse.urljoin(response.url,post_url),meta={'front_image_url':image},callback=self.parse_detail)#reques callback参数是要传函数
        next_url = response.css('.next.page-numbers ::attr(href)').extract_first('')
        if next_url:
            yield  Request(next_url,callback=self.parse)
    def parse_detail(self,response):
        # article = JobBoleArticleItem()
        #
        # '''提取文章详情页，作为回调函数'''
        # title = response.xpath('//div[@class="entry-header"]/h1/text()').extract()[0]
        # create_data = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/text()').extract()[0].replace('·','').strip()
        # praise_nums = response.xpath('//span[contains(@class,"vote-post-up")]/h10/text()').extract()[0]
        # fav_nums = response.xpath('//span[contains(@class,"bookmark-btn")]/text()').extract()[0]
        # comment_nums = response.xpath("//a[@href='#article-comment']/span/text()").extract()[0]
        # comment_re = re.match(".*?(\d+).*", comment_nums)
        # if comment_re:
        #     comment_nums = int(comment_re.group(1))
        # else:
        #     comment_nums = 0
        # fav_re = re.match(".*?(\d+).*",fav_nums)
        # if fav_re:
        #     fav_nums = int(fav_re.group(1))
        # else:
        #     fav_nums = 0
        front_image_url = response.meta.get('front_image_url','')
        # content = response.xpath("//div[@class='entry']").extract()[0]
        # tag_list = response.xpath("//p[@class='entry-meta-hide-on-mobile']/a/text()").extract()
        # tag_list = [element for element in tag_list if not element.strip().endswith('评论')]
        # tags = ','.join(tag_list)
        #
        # #进行存储
        # article['url_object_id'] = get_md5(response.url)
        # article['title'] = title
        # article['url'] = response.url
        # try:
        #     create_data = datetime.datetime.strptime(create_data,'%Y/%m/%d').date()
        # except Exception as e:
        #     create_data = datetime.datetime.now().date()
        # article['create_data'] = create_data
        # article['front_image_url'] = [front_image_url]
        # article['praise_nums'] = praise_nums
        # article['comment_nums'] = comment_nums
        # article['fav_nums'] = fav_nums
        # article['tags'] = tags
        # article['content'] = content

    # 通过ItemLoader加载item
        Item_Loader = ArticleSpiderItem(item=JobBoleArticleItem(),response=response)
        # Item_Loader.add_css()
        # Item_Loader.add_xpath()
        # Item_Loader.add_value()
        front_image_url = response.meta.get('front_image_url', '')
        Item_Loader.add_css('title','.entry-header h1::text')
        Item_Loader.add_value('url', response.url)
        Item_Loader.add_value('url_object_id',get_md5(response.url))
        Item_Loader.add_value('front_image_url',[front_image_url])
        Item_Loader.add_css('create_data','.entry-meta-hide-on-mobile::text')
        Item_Loader.add_css('praise_nums','.vote-post-up h10::text')
        Item_Loader.add_css('fav_nums','.bookmark-btn::text')
        Item_Loader.add_css('comment_nums','a[href="#article-comment"] span::text')
        Item_Loader.add_css('content','div.entry')
        Item_Loader.add_css('tags','p.entry-meta-hide-on-mobile a::text')

        article = Item_Loader.load_item()#必须调用才会进行解析
        yield article



        # css
        # title =  response.css('.entry-header h1::text').extract()[0]
        # create_data = response.css('.entry-meta-hide-on-mobile::text').extract()[0].replace('·','').strip()
        # praise_nums = response.css('.vote-post-up h10::text').extract()[0]
        # fav_nums =  response.css('.bookmark-btn::text').extract()[0]
        # if fav_re:
        #     fav_nums = fav_re.group(1)
        # else:
        #     fav_nums = 0
        # comment_nums = response.css('a[href="#article-comment"] span::text').extract()[0]
        # content = response.css('div.entry').extract()[0]
        # tag_list =response.css('p.entry-meta-hide-on-mobile a::text').extract()[0]
        # tag_list = [element for element in tag_list if not element.strip().endswith('评论')]
        # tags = ','.join(tag_list)
