# -*- coding: utf-8 -*-
import scrapy
from selenium import webdriver
from lxml import etree
from scrapy_splash import SplashRequest
import requests
import json
import re
from weibo_crawl.items import *

class WeiboSpider(scrapy.Spider):
    name = 'weibo'
    allowed_domains = ['*']
    n = 1
    start_urls = 'http://s.weibo.com/weibo/历史&page={}'
    headers = {
            'Host': ' weibo.com',
            'User-Agent': ' Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36',
            'Cookie': ' SINAGLOBAL=2360009592437.642.1515925269024; UM_distinctid=1611760e10f42f-0269380fc27ac9-e323462-1fa400-1611760e110a3b; login_sid_t=e54b72f6d4d22841efe0c6ecbcc1fd24; cross_origin_proto=SSL; _s_tentry=passport.weibo.com; UOR=v.baidu.com,widget.weibo.com,www.baidu.com; Apache=6032352707535.143.1527236977800; ULV=1527236977806:6:1:1:6032352707535.143.1527236977800:1521199141848; SSOLoginState=1527237016; un=lixuechen198@sina.com; wvr=6; ALF=1558774656; SCF=AnR9uXXHLFnmfyn04YYuIWzolbXPdLkwNrttXSQcV5kdjqvmt_BDwPuDQ5q3loAn7P7GE1jFaPGoPHee5jIJmYA.; SUB=_2A252A6BQDeRhGedI7lMT-CbNzj-IHXVVeJaYrDV8PUNbmtANLUHxkW9NVyxXn44fdweqQdoJpLylmR1uTPOKrAAw; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WW-_B2WnJrV56zbd8dPCFAL5JpX5KzhUgL.Fo2cSK2E1hnpSKe2dJLoI79jwsep1Knt; SUHB=0M2ETEGGaB-arT',
        }
    def start_requests(self):
        yield SplashRequest(self.start_urls.format(1), self.detail_parse,splash_headers=self.headers,args={'wait':1})
    def detail_parse(self,response):
        if self.n == 5:
            return
        item = WeiboItem()
        info = response.xpath('//div[@action-type="feed_list_item"]')
        api = 'http://s.weibo.com/ajax/direct/morethan140?mid={mid}&search={word}&current_uid={uid}'
        for i in info:
            name = i.xpath('.//div[contains(@class,"feed_content")]/a/text()').extract_first(default='暂无').strip()
            content = ''.join(i.xpath('.//div[contains(@class,"feed_content")]//p[@class="comment_txt"]//text()').extract()).replace("\n\t",'').replace('\u200b','').replace('\n','').strip()
            if '展开全文c' in content:
                mid = i.xpath('./@mid').extract_first()
                uid = i.xpath('./@tbinfo').extract_first().split('=')[1]
                full_api = api.format(mid=mid,word='国家',uid=uid)
                content = json.loads(requests.get(full_api).text)['data']['html'].replace('\u200b','').replace('\t','')
                pat = re.compile(r'<.*?>.*?<.*?>')
                content = pat.sub('',content).strip()
            item['name'] = name
            item['content'] = content
            yield item
        self.n += 1
        print(self.start_urls.format(self.n))
        yield SplashRequest(self.start_urls.format(self.n),self.detail_parse,splash_headers=self.headers,args={'wait':1},dont_filter=True)
