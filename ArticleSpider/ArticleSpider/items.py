# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
import datetime
import scrapy
import re
from scrapy.loader.processors import MapCompose,TakeFirst,Join
from scrapy.loader import ItemLoader

from .utils.common import extract_num
from .settings import SQL_DATA_FORMAT,SQL_DATETIME_FORMAT
from w3lib.html import remove_tags
class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


def date_convert(value):
    try:
        value_date = value[0].replace('·','').strip()
        create_data = datetime.datetime.strptime(value_date,'%Y/%m/%d').date()
    except Exception as e:
        create_data = datetime.datetime.now().date()
    return create_data


def get_nums(value):
    nums_re = re.match(".*?(\d+).*", value)
    if nums_re:
        value = int(nums_re.group(1))
    else:
        value = 0
    return value


def remove_comment_tags(value):
    '''去掉tags提取的评论'''
    if '评论' in value:
        return ''
    else:
        return value


def return_value(value):
    '''返回url,覆盖default loader'''
    return value

class ArticleSpiderItem(ItemLoader):
    '''自定义itemloader'''
    default_output_processor = TakeFirst()


class JobBoleArticleItem(scrapy.Item):
    title = scrapy.Field(
    )
    create_data = scrapy.Field(
        input_processor=MapCompose(date_convert),

    )
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    front_image_url = scrapy.Field(
        output_processor=MapCompose(return_value)
    )
    front_image_path = scrapy.Field()#本地存储路劲
    praise_nums = scrapy.Field(
        input_processor=MapCompose(get_nums),
    )
    comment_nums = scrapy.Field(
        input_processor=MapCompose(get_nums),
    )
    fav_nums = scrapy.Field(
        input_processor=MapCompose(get_nums),
    )
    tags = scrapy.Field(
        input_processor = MapCompose(remove_comment_tags),
        output_processor = Join(',')
    )
    content = scrapy.Field()

    def get_insert_sql(self):
        '''插入伯乐在线表sql语句'''
        insert_sql = '''
                insert into article_spider(title,create_data,url,url_object_id,front_image_url,front_image_path,praise_nums,comment_nums,fav_nums,tags,
                content) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE praise_nums=VALUES(praise_nums),comment_nums=VALUES(comment_nums),fav_nums=VALUES(fav_nums)'''
        params = (self['title'], self['create_data'], self['url'], self['url_object_id'], self['front_image_url'],
                  self['front_image_path'], self['praise_nums'], self['comment_nums'], self['fav_nums'], self['tags'],
                  self['content'])
        return insert_sql,params

class ZhihuQuestionItem(scrapy.Item):
    '''知乎问题'''
    zhihu_id = scrapy.Field()
    topics = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    answer_num = scrapy.Field()
    comment_num = scrapy.Field()
    click_num = scrapy.Field()
    watch_user_num = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        '''插入知乎question表的sql语句'''
        insert_sql = '''
        insert into zhihu_question(zhihu_id,topics,url,title,content,answer_num,comment_num,watch_user_num,click_num,
        crawl_time) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE answer_num=VALUES(answer_num),comment_num=VALUES(comment_num),watch_user_num=VALUES(watch_user_num),click_num=VALUES(click_num)
        '''
        # zhihu_id = ''.join(self.zhihu_id)
        zhihu_id = self['zhihu_id'][0]
        topics = ','.join(self['topics'])
        url = ''.join(self['url'])
        title = ''.join(self['title'])
        content = ''.join(self['content'])
        answer_num = extract_num(''.join(self['answer_num']))
        comment_num = extract_num(''.join(self['comment_num']))
        watch_user_num = extract_num(self['click_num'][0])
        click_num = extract_num(self['click_num'][1])
        crawl_time = datetime.datetime.now().strftime(SQL_DATETIME_FORMAT)#转换成字符串
        params = (zhihu_id,topics,url,title,content,answer_num,comment_num,watch_user_num,click_num,crawl_time)

        return insert_sql,params

class ZhihuAnswerItem(scrapy.Item):
    '''知乎问题回答'''
    zhihu_id = scrapy.Field()
    url = scrapy.Field()
    question_id = scrapy.Field()
    author_id = scrapy.Field()
    content = scrapy.Field()
    parise_num = scrapy.Field()
    comment_num = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
    crawl_time = scrapy.Field()
    def get_insert_sql(self):
        '''插入知乎answer表的sql语句'''
        insert_sql = '''
                insert into zhihu_answer(zhihu_id,url,question_id,author_id,content,praise_num,comment_num,create_time,update_time,
                crawl_update_time)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE content=VALUES(content),praise_num=VALUES(praise_num),comment_num=VALUES(comment_num),
                update_time=VALUES(update_time)
                '''

        create_time = datetime.datetime.fromtimestamp(self['create_time']).strftime(SQL_DATETIME_FORMAT)
        update_time = datetime.datetime.fromtimestamp(self['update_time']).strftime(SQL_DATETIME_FORMAT)
        params = (
            self['zhihu_id'],self['url'],self['question_id'],self['author_id'],self['content'],self['parise_num'],
            self['comment_num'],create_time,update_time,self['crawl_time'].strftime(SQL_DATETIME_FORMAT),
        )
        return insert_sql,params


class LoagouJobItemLoader(ItemLoader):
    '''自定义itemloader'''
    default_output_processor = TakeFirst()


def remove_splash(value):
    '''去掉/'''
    return value.replace('/','')


def handle_jobaddr(value):
    '''去除上班地点的查看地图和\n'''
    addr_list = value.split('\n')
    addr_list = [item.strip() for item in addr_list if item.strip()!='查看地图']
    return ''.join(addr_list)

class LoagouJobItem(scrapy.Item):
    '''拉勾网职位信息'''
    title = scrapy.Field()
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    salary = scrapy.Field()
    job_city = scrapy.Field(
        input_processor = MapCompose(remove_splash)
    )
    work_years = scrapy.Field(
        input_processor = MapCompose(remove_splash)
    )
    degree_need = scrapy.Field(
        input_processor = MapCompose(remove_splash)
    )
    job_type = scrapy.Field()
    publish_time = scrapy.Field()
    tags = scrapy.Field(input_processor = Join(','))
    job_advartage = scrapy.Field()
    job_desc = scrapy.Field(

    )
    job_addr = scrapy.Field(
        input_processor=MapCompose(remove_tags,handle_jobaddr)
    )
    company_url = scrapy.Field()
    company_name = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):

        insert_sql = '''
        insert into lagou_job(title,url,url_object_id,salary,job_city,work_years,degree_need,
        job_type,publish_time,tags,job_advartage,job_desc,job_addr,company_url,company_name,crawl_time)   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
        %s,%s,%s,%s)
        '''
        params=(self['title'],self['url'],self['url_object_id'],self['salary'],self['job_city'],self['work_years'],self['degree_need'],
        self['job_type'],self['publish_time'],self['tags'],self['job_advartage'],self['job_desc'],self['job_addr'],self['company_url'],self['company_name'],self['crawl_time'])
        return insert_sql,params


class DingdianItemLoad(ItemLoader):
    '''改变默认输出'''
    default_output_processor = TakeFirst()


def get_title(value):
    title = value.split(' ')
    return title


def get_num(value):
    num = re.match(r'.*/(\d+)',value)
    if num:
        return num.group(1)
    return value


def get_num_article(value):
    num = value.replace('字','')
    return int(num)


def get_num_int(value):
    return int(value)


def get_datetime(value):
    update_time =datetime.datetime.strptime(value.replace('\xa0',''),'%Y-%m-%d')
    return update_time

class DingdianItem(scrapy.Item):
    article_type = scrapy.Field()
    article_id = scrapy.Field(
        input_processor=MapCompose(get_num)
    )
    title = scrapy.Field(
        input_processor=MapCompose(get_title)
    )
    fav_nums = scrapy.Field(
        input_processor = MapCompose(get_num_int)
    )
    total_click_nums = scrapy.Field(
        input_processor=MapCompose(get_num_int)
    )#总点击数
    recommend_nums = scrapy.Field(
        input_processor=MapCompose(get_num_int)
    )#总推荐数量
    author = scrapy.Field()
    article_len = scrapy.Field(
        input_processor=MapCompose(get_num_article)
    )
    month_click_nums = scrapy.Field(
        input_processor=MapCompose(get_num_int)
    )#本月点击数
    month_fav_nums = scrapy.Field(
        input_processor=MapCompose(get_num_int)
    )#本月推荐数
    article_status = scrapy.Field()#状态
    update_time= scrapy.Field(
        input_processor = MapCompose(get_datetime)
    )#更新时间
    week_click_nums = scrapy.Field(
        input_processor=MapCompose(get_num_int)
    )
    week_fav_nums = scrapy.Field(
        input_processor=MapCompose(get_num_int)
    )
    crawl_time = scrapy.Field(

    )

    def get_insert_sql(self):
        '''ON DUPLICATE KEY UPDATE fav_nums=VALUES(fav_nums),total_click_nums=VALUES (total_click_nums),recommend_nums=VALUES (recommend_nums),article_len=VALUES (article_len),month_click_nums=VALUES (month_click_nums)
        month_fav_nums=VALUES (month_fav_nums),article_status=VALUES (article_status),update_time=VALUES (update_time),week_fav_nums=VALUES (week_fav_nums),crawl_time=VALUES (crawl_time)'''
        insert_sql ='''insert into dingdian(article_type,article_id,title,fav_nums,total_click_nums,recommend_nums,author,article_len,month_click_nums,month_fav_nums,article_status,update_time,week_click_nums,week_fav_nums,crawl_time) 
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)ON DUPLICATE KEY UPDATE fav_nums=VALUES(fav_nums),total_click_nums=VALUES (total_click_nums),recommend_nums=VALUES(recommend_nums),article_len=VALUES(article_len),month_click_nums=VALUES(month_click_nums),
        month_fav_nums=VALUES(month_fav_nums),article_status=VALUES(article_status),update_time=VALUES (update_time),week_fav_nums=VALUES(week_fav_nums),crawl_time=VALUES(crawl_time)'''
        params = (self['article_type'],self['article_id'],self['title'],self['fav_nums'],self['total_click_nums'],self['recommend_nums'],self['author'],self['article_len'],self['month_click_nums'],self['month_fav_nums'],self['article_status'],self['update_time'],self['week_click_nums'],self['week_fav_nums'],self['crawl_time'])
        return insert_sql,params