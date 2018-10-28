# -*- coding: utf-8 -*-
"""
这个爬虫用来抓取boss中的列表页面以及详情页面=
"""

import logging
import random
import json

from scrapy import Spider
from scrapy import Request
from urllib.parse import quote_plus
from lxml import etree

from zhaopin.items import JobItem

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)
date_format = '%Y-%m-%d %H:%M:%S'

city_ids = {101010100: u"北京"}
key_words = ["实习"]
list_url_tem = "https://www.zhipin.com/c101010100/?query={kw}&page={pg}&ka=page-{pg1}"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome Safari/537.36",
}


class ZhiPin(Spider):
    name = "boss_web"
    custom_settings = {
        "DOWNLOAD_DELAY": 3,
        "COOKIES_ENABLED": False,
        "DOWNLOAD_TIMEOUT": 15,
        "DOWNLOADER_MIDDLEWARES": {
            # 'zhaopin.middlewares.RandomProxyMiddleware': 100,
        },
    }

    def start_requests(self):
        for kw in key_words:
            for cid, name in city_ids.items():
                url = list_url_tem.format(kw=quote_plus(kw), cid=cid, pg=1, pg1=1)
                logger.info("will crawl url {}".format(url))
                # yield Request(url=url, callback=self.parse_list, priority=6,
                #               meta={"city": name, "kw": kw, "cid": cid, "pg": 1},
                #               headers={"X-Forward-For": random_ip()})

    def parse_list(self, response):
        logger.info("job list url {}".format(response.url))
        kw = response.meta["kw"]
        cid = response.meta["cid"]
        city = response.meta["city"]
        pg = response.meta["pg"]

        from IPython import embed
        embed()
        for cell in response.xpath('//div[@class="job-list"]/ul/li'):
            detail_url = response.urljoin(cell.xpath('.//a/@href').extract_first())
            logger.info("will crawl detail {}".format(detail_url))
            yield Request(url=detail_url, callback=self.parse_detail, priority=1,
                          meta=response.meta, headers={"X-Forward-For": random_ip()})

            # if pg < 10:
            #     pg = pg + 1
            #     next_url = list_url_tem.format(kw=quote_plus(kw), cid=cid, pg=pg)
            #     logger.info("will crawl url {}".format(next_url))
            #     yield Request(url=next_url, callback=self.parse_list, priority=6,
            #                   meta={"city": city, "kw": kw, "cid": cid, "pg": pg},
            #                   headers={"X-Forward-For": random_ip()})

    def parse_detail(self, response):
        logger.info("job detail url {}".format(response.url))
        # from IPython import embed
        # embed()
        post_item = JobItem({
            "city": response.meta["city"],
            "job_name": response.xpath('//div[@class="job-banner"]/div[@class="name"]/text()').extract_first(),
            "job_url": response.url,
            "publish_time": response.xpath('//script[@type="application/ld+json"]').re_first(
                "\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"),
            "company_name": response.xpath(
                '//a[@class="job-company"]/div[@class="info-primary"]/div[@class="name"]/text()').extract_first(),
            "job_salary": response.xpath('//span[@class="salary"]/text()').extract_first(),
            "job_exp": response.xpath('//div[@class="job-banner"]/p/text()').extract()[1],
            "job_edu": response.xpath('//div[@class="job-banner"]/p/text()').extract()[2],
            "job_sec": response.xpath('normalize-space(//div[@class="job-sec"]/div[@class="text"])').extract_first(),
            "job_tags": response.xpath('//div[@class="job-tags"]/span[not(contains(@class, "time"))]/text()').extract(),
            "job_publisher_name": response.xpath(
                '//div[@class="job-author"]//div[@class="name"]/text()').extract_first(),
            "job_publisher_post": response.xpath('//div[@class="job-author"]//p[@class="gray"]/text()').extract()[1],
        })
        logger.info(u"crawled {}".format(post_item))
        yield post_item


def random_ip():
    return "201.{}.{}.{}".format(random.randrange(256), random.randrange(256), random.randrange(256))
