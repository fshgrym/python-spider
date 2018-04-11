# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html
from ArticleSpider.tools.crawl_xici_ip import GetIp
from scrapy import signals
from fake_useragent import UserAgent
from selenium import webdriver
from scrapy.http import HtmlResponse


class ArticlespiderSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class RandownUserAgentMiddlware(object):
    '''随机更换user_agent'''
    def __init__(self,crawler):
        super(RandownUserAgentMiddlware, self).__init__()
        self.ua = UserAgent()
        self.ua_type = crawler.settings.get('RANDOM_UA_TYPE','random')

    @classmethod
    def from_crawler(cls,crawler):
        return cls(crawler)

    def process_request(self,request,spider):
        def get_ua():
            '''getattr的用法，取self.ua的某个属性，方法'''
            return getattr(self.ua,self.ua_type)
        random_ua_agent = get_ua()
        request.headers.setdefault('User-Agent',get_ua())
        # request.meta['proxy'] = 'http://192.168.1.1:8080'


class RanDomProxyMiddleware(object):
    def process_request(self, request, spider):
        random_ip = GetIp()
        request.meta['proxy'] = random_ip.get_random()


class JsPageMiddleware(object):
    '''通过selenium集成到scrapy'''
    def process_request(self,request,spider):
        if spider.name == 'jobbole':
            spider.browser.get(request.url)
            import time
            time.sleep(3)
            #声明这个url不需要再次下载
            return HtmlResponse(url=spider.browser.current_url,body=spider.browser.page_source,encoding='utf-8',request=request)
# 无界面浏览器
# pip install pyvirtualdisplay
# from pyvirtualdisplay import Display
# display = Display(visible=0,size=(800,600))
# display.start()
# browser = webdriver.Chrome()
# browser.get()
#无界面浏览器

