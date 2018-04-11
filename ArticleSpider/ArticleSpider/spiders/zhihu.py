# -*- coding: utf-8 -*-
import scrapy
import re, time, os, json, datetime
from PIL import Image
from urllib import parse
from scrapy.loader import ItemLoader
from ..items import ZhihuQuestionItem, ZhihuAnswerItem


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['https://www.zhihu.com/']
    # question的answer的api接口，url请求
    start_answer_url = 'https://www.zhihu.com/api/v4/questions/{0}/answers?sort_by=default&include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cupvoted_followees%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%3F%28type%3Dbest_answerer%29%5D.topics&limit={1}&offset={2}'

    def parse(self, response):
        '''提取出页面所有的url，并跟进爬取，默认深度优先算法
        如果提取的url中样式为/question/xxx我们就直接解析下载
        '''
        all_urls = response.css('a::attr(href)').extract()
        all_urls = [parse.urljoin(response.url, url) for url in all_urls]
        for url in all_urls:
            math_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", url)
            if math_obj:
                request_url = math_obj.group(1)
                quetion_url = math_obj.group(2)
                yield scrapy.Request(request_url, headers=self.header, callback=self.parse_question)
            else:
                yield scrapy.Request(url, headers=self.header)

    def parse_question(self, response):
        '''处理parse传过来的question，处理页面中的question，item'''
        math_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", response.url)
        if math_obj:
            quetion_id = int(math_obj.group(2))
        item_loader = ItemLoader(item=ZhihuQuestionItem(), response=response)
        item_loader.add_css('title', 'h1.QuestionHeader-title::text')
        item_loader.add_css('content', 'div.QuestionHeader-detail')
        item_loader.add_value('url', response.url)
        item_loader.add_value('zhihu_id', quetion_id)
        item_loader.add_css('answer_num', '.List-headerText span::text')
        item_loader.add_css('comment_num', 'div.QuestionHeader-Comment button::text')
        item_loader.add_css('click_num', '.NumberBoard-value::text')
        item_loader.add_css('topics', '.QuestionHeader-tags .Popover div::text')

        Question_item = item_loader.load_item()
        yield scrapy.Request(self.start_answer_url.format(quetion_id, 20, 0), headers=self.header,
                             callback=self.parse_answer)
        yield Question_item

    def parse_answer(self, response):
        '''answert处理函数'''
        ans_json = json.loads(response.text)
        is_end = ans_json['paging']['is_end']
        totals_answer = ans_json['paging']['totals']
        next_url = ans_json['paging']['next']

        # 提取
        for answer in ans_json['data']:
            answer_item = ZhihuAnswerItem()
            answer_item['zhihu_id'] = answer['id']
            answer_item['url'] = answer['url']
            answer_item['question_id'] = answer['question']['id']
            answer_item['author_id'] = answer['author']['id'] if 'id' in answer['author'] else None
            answer_item['content'] = answer['content'] if 'content' in answer else None
            answer_item['parise_num'] = answer['voteup_count']
            answer_item['comment_num'] = answer['comment_count']
            answer_item['create_time'] = answer['created_time']
            answer_item['update_time'] = answer['updated_time']
            answer_item['crawl_time'] = datetime.datetime.now()
            yield answer_item
        if not is_end:
            yield scrapy.Request(next_url, headers=self.header, callback=self.parse_answer)

    def start_requests(self):
        return [scrapy.Request('https://www.zhihu.com/', headers=self.header, callback=self.login)]

    header = {
        'Host': 'www.zhihu.com',
        'Origin': 'https://www.zhihu.com',
        'Pragma': 'no-cache',
        'Referer': 'https://www.zhihu.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.3 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',

    }

    def login(self, response):
        '''控制入口，重写start_requests'''
        response_text = response.text
        match_obj = re.findall('.*name="_xsrf" value="(.*?)"', response_text)
        if match_obj:
            xsrf = match_obj[0]
        if xsrf:
            post_data = {
                '_xsrf': xsrf,
                'password': '***********',
                'phone_num': '183127433**',
                'captcha': ''
            }
        t = str(int(time.time() * 1000))
        yield scrapy.Request('http://www.zhihu.com/captcha.gif?r=' + t + "&type=login", headers=self.header,
                             meta={'post_data': post_data}, callback=self.get_captcha)

    def check_login(self, response):
        '''判断是否登录成功'''
        text_json = json.loads(response.text)
        if 'msg' in text_json and text_json['msg'] == '登录成功':
            for url in self.start_urls:
                print('登录成功')
                yield scrapy.Request(url, dont_filter=True, headers=self.header, callback=self.parse)
        else:
            print('登录失败')

    def get_captcha(self, response):
        with open('captcha.jpg', 'wb') as f:
            f.write(response.body)
            f.close()
            # 用pillow 的 Image 显示验证码
            # 如果没有安装 pillow 到源代码所在的目录去找到验证码然后手动输入
        try:
            im = Image.open('captcha.jpg')
            im.show()
            captcha = input("please input the captcha>")
            im.close()
        except:
            print(u'请到 %s 目录找到captcha.jpg 手动输入' % os.path.abspath('captcha.jpg'))
            captcha = input("please input the captcha>")
        post_data = response.meta.get('post_data', {})
        post_data['captcha'] = captcha
        return [scrapy.FormRequest(
            url='https://www.zhihu.com/login/phone_num',
            formdata=post_data,
            headers=self.header,
            callback=self.check_login,

        )]
