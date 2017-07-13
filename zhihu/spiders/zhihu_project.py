# -*- coding: utf-8 -*-
import json

import scrapy

from zhihu.items import ZhihuItem


class ZhihuProjectSpider(scrapy.Spider):
    name = 'zhihu_project'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']

    start_user = 'excited-vczh'
    user_url = 'https://www.zhihu.com/api/v4/members/{user}?include={include}'
    user_include = 'allow_message,is_followed,is_following,is_org,is_blocking,employments,answer_count,follower_count,articles_count,gender,badge[?(type=best_answerer)].topics'
    follow_url = 'https://www.zhihu.com/api/v4/members/{user}/followees?include={include}&offset={offset}&limit={limit}'
    follow_include= 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'


    def start_requests(self):
        # url = 'https://www.zhihu.com/api/v4/members/excited-vczh/followees?include=data%5B*%5D.answer_count%2Carticles_count%2Cgender%2Cfollower_count%2Cis_followed%2Cis_following%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics&offset=60&limit=20'
        # url = 'https://www.zhihu.com/api/v4/members/yang-yu-ting-7-23?include=allow_message%2Cis_followed%2Cis_following%2Cis_org%2Cis_blocking%2Cemployments%2Canswer_count%2Cfollower_count%2Carticles_count%2Cgender%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics'
        yield scrapy.Request(self.user_url.format(user=self.start_user, include=self.user_include), callback=self.parse_user)

        yield scrapy.Request(self.follow_url.format(user=self.start_user, include=self.follow_include, offset=0, limit=20),callback=self.parse_follows)


    def parse_user(self, response):
        result = json.loads(response.text)
        item = ZhihuItem()
        for field in item.fields:
            if field in result.keys():
                item[field] = result.get(field)
        yield item
        yield scrapy.Request(url=self.follow_url.format(user=result.get('url_token'), include=self.follow_include, offset=0, limit=20), callback=self.parse_follows)


    def parse_follows(self, response):
        result = json.loads(response.text)

        if 'data' in result.keys():
            for result_data in result.get('data'):
                yield scrapy.Request(url=self.user_url.format(user=result_data.get('url_token'), include=self.user_include), callback=self.parse_user)

        if 'paging' in result.keys():
            next_page = result.get('paging').get('next')
            yield scrapy.Request(url=next_page, callback=self.parse_follows)
        else:
            self.logger.error('Error')

    # def parse(self, response):
    #     print(response.text)
