# coding:utf-8
import logging
import random
import json
import dateformatting

from scrapy import Spider
from scrapy import Request
from urllib.parse import quote_plus

from zhaopin.items import JobShortItem

from zhaopin.spider_conf import directions, key_words, date_format

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)

city_ids = {"010000": "北京", "020000": "上海", "080200": "杭州", "040000": "深圳", "030200": "广州"}

list_url_tem = "https://search.51job.com/list/{cid},000000,0000,00,9,99,{kw},2,1.html?" \
               "lang=c&stype=&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&" \
               "providesalary=99&lonlat=0%2C0&radius=-1&ord_field=0&confirmdate=9&fromType=&dibiaoid=0&" \
               "address=&line=&specialarea=00&from=&welfare="

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/69.0.3497.81 Safari/537.36",
}


class QianchengJob(Spider):
    name = "51job_web"
    custom_settings = {
        "DOWNLOAD_DELAY": 5,
        "COOKIES_ENABLED": False,
        "DOWNLOAD_TIMEOUT": 30,
        "DOWNLOADER_MIDDLEWARES": {
            # 'zhaopin.middlewares.RandomProxyMiddleware': 100,
        },
        "ITEM_PIPELINES": {
            # 'zhaopin.pipelines.JobPipeline': 300,
        },
    }

    def start_requests(self):
        for direct in directions:
            for kw in key_words:
                for cid, city in city_ids.items():
                    url = list_url_tem.format(cid=cid, kw=quote_plus(direct + kw))
                    pg = 1
                    logger.info("will crawl key word  {}".format(kw))
                    yield Request(url=url, callback=self.parse_list, priority=6,
                                  meta={"cid": cid, "kw": kw, "pg": pg, "direct": direct}, headers=headers)

    def parse_list(self, response):
        logger.info("job list url {}".format(response.url))
        kw = response.meta["kw"]
        cid = response.meta["cid"]
        pg = response.meta["pg"]
        direct = response.meta["direct"]

        timeout_date = self.timeout_date
        timeout = False

        content = response.xpath('//div[@class="dw_table"]/div[@class="el"]')
        if not content.get('content'):
            print("debug")
            from IPython import embed
            embed()

        for cell in content:
            post_item = JobShortItem()
            time_it = cell.xpath('./span[@class="t5"]/text()').extract_first()
            date = dateformatting.parse(time_it)
            if date and date < timeout_date:
                timeout = True
                logger.info("Timeout: %s < %s" % (date, timeout_date))
                break
            post_item["job_name"] = cell.xpath('./p[starts-with(@class, "t1")]//a/@title').extract_first()
            post_item["url"] = cell.xpath('./p[starts-with(@class, "t1")]//a/@href').extract_first()
            post_item["city"] = city_ids[cid]
            post_item["source"] = "51job"
            post_item["district"] = cell.xpath('./span[@class="t3"]/text()').extract_first()
            salary = cell.xpath('./span[@class="t4"]/text()').extract_first()
            post_item["month_salary"] = salary if salary else "面议"
            post_item["day_salary"] = ""
            post_item["job_direction"] = directions[direct]
            post_item["job_exp"] = ""
            post_item["job_edu"] = ""
            post_item["publish_man"] = ""
            post_item["publish_man_post"] = ""
            post_item["publish_time"] = dateformatting.parse(time_it).strftime(date_format)
            post_item["company_name"] = cell.xpath('./span/a/@title').extract_first()
            post_item["company_addr"] = cell.xpath('./span[@class="t3"]/text()').extract_first()
            post_item["company_industry"] = ""
            logger.info("crawled list {} {}".format(post_item["url"], post_item["job_name"]))
            yield post_item
        next_page = response.xpath('//div[@class="rt"]/a/@href').extract_first()
        if next_page and not timeout:
            pg = pg + 1
            url = next_page
            logger.info("will crawl url {}".format(url))
            yield Request(url=url, callback=self.parse_list, priority=6,
                          meta={"cid": cid, "kw": kw, "pg": pg, "direct": direct}, headers=headers)

    @property
    def timeout_date(self):
        return dateformatting.parse("10天前")

