# -*- coding: utf-8 -*-

"""
这个爬虫用来抓取boss中的列表页面
"""
import logging
import random
import datetime

from scrapy import Spider
from scrapy import Request
from urllib.parse import quote_plus

from zhaopin.items import JobShortItem

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)
date_format = '%Y-%m-%d %H:%M:%S'
day_format = '%Y-%m-%d'

city_ids = {101010100: u"北京",
            101020100: u"上海",
            101280100: u"广州",
            101210100: u"杭州",
            101280600: u"深圳",
            }
# city_ids = {101010100: u"北京"}
key_words = {"java": 1, "python": 4, "C++": 2, "数据挖掘": 6, "android": 7,
             "ios": 8, "测试": 10, "web": 3, "运维": 9, "php": 5}

list_url_tem = "https://www.zhipin.com/c{cid}/?query={kw}&page={pg}&ka=page-{pg1}"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome Safari/537.36",
}


class ZhiPin(Spider):
    name = "boss_web_list"
    custom_settings = {
        "DOWNLOAD_DELAY": 3,
        "COOKIES_ENABLED": False,
        "DOWNLOAD_TIMEOUT": 15,
        "DOWNLOADER_MIDDLEWARES": {
            # 'zhaopin.middlewares.RandomProxyMiddleware': 100,
        },
        "ITEM_PIPELINES": {
            'zhaopin.pipelines.JobPipeline': 300,
        },
    }

    def start_requests(self):
        for kw in key_words.keys():
            for cid, name in city_ids.items():
                url = list_url_tem.format(kw=quote_plus(kw+"实习"), cid=cid, pg=1, pg1=1)
                logger.info("will crawl url {}".format(url))
                yield Request(url=url, callback=self.parse_list,
                              meta={"city": name, "kw": kw, "cid": cid, "pg": 1},
                              headers=headers)

    def parse_list(self, response):
        logger.info("job list url {}".format(response.url))
        kw = response.meta["kw"]
        cid = response.meta["cid"]
        city = response.meta["city"]
        pg = response.meta["pg"]
        content = response.xpath('//div[@class="job-list"]/ul/li')
        for cell in content:
            post_item = JobShortItem()
            post_item["city"] = response.meta["city"]
            post_item["job_name"] = cell.xpath('.//div[@class="job-title"]/text()').extract_first()
            post_item["source"] = "boss直聘"
            post_item["job_direction"] = key_words[kw]
            post_item["url"] = response.urljoin(cell.xpath('.//a/@href').extract_first())
            p_time = cell.xpath('.//div[@class="info-publis"]//p/text()').re_first("发布于(.*?)$")
            if ":" in p_time:
                post_item["publish_time"] = datetime.datetime.now().strftime(day_format)
            else:
                post_item["publish_time"] = "{}-{}".format(datetime.date.today().year,
                                                           p_time.replace("月", "-").replace("日", ""))
            post_item["company_name"] = cell.xpath('.//div[@class="info-company"]//a/text()').extract_first()
            post_item["company_industry"] = cell.xpath('.//div[@class="company-text"]/p/text()').extract_first()
            post_item["month_salary"] = cell.xpath(
                './/div[@class="info-primary"]//span[@class="red"]/text()').extract_first()
            job_info = cell.xpath('.//div[@class="info-primary"]/p/text()').extract()
            post_item["company_addr"], post_item["job_exp"], post_item["job_edu"] = job_info
            post_item["district"] = post_item["company_addr"]
            pubisher_info = cell.xpath('.//div[@class="info-publis"]/h3/text()').extract()
            post_item["publish_man"], post_item["publish_man_post"] = pubisher_info
            logger.info("crawled list {} {}".format(post_item["url"], post_item["job_name"]))
            yield post_item

            if len(content) == 30:
                pg = pg + 1
                next_url = list_url_tem.format(kw=quote_plus(kw+"实习"), cid=cid, pg=pg, pg1=pg)
                logger.info("will crawl url {}".format(next_url))
                yield Request(url=next_url, callback=self.parse_list,
                              meta={"city": city, "kw": kw, "cid": cid, "pg": pg}, headers=headers)


def random_ip():
    return "201.{}.{}.{}".format(random.randrange(256), random.randrange(256), random.randrange(256))
