# coding:utf-8
import logging
import random
import json
import dateformatting

from scrapy import Spider
from scrapy import FormRequest

from zhaopin.items import JobShortItem

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)
date_format = '%Y-%m-%d %H:%M:%S'

city_ids = {101010100: "北京",
            101010101: "上海",
            101010102: "西安",
            101010103: "杭州",
            101010104: "深圳",
            101010105: "广州"
            }
key_words = {"java": 1, "python": 4, "C++": 2, "数据挖掘": 6, "android": 7,
             "ios": 8, "测试": 10, "web": 3, "运维": 9, "php": 5}
list_url_tem = "https://www.lagou.com/jobs/positionAjax.json?city={ct}&needAddtionalResult=false"
# list_url_tem = "https://www.lagou.com/jobs/positionAjax.json?needAddtionalResult=false"
detail_url = "https://www.lagou.com/jobs/{}.html"

headers = {
    "Host": "www.lagou.com",
    "Connection": "Keep-alive",
    "Origin": "https://www.lagou.com",
    "X-Anit-Forge-Code": "0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
    "X-Anit-Forge-Token": "None",
    "Referer": "https://www.lagou.com/jobs/list_java%E5%AE%9E%E4%B9%A0?labelWords=sug&fromSearch=true&suginput=java",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh,en;q=0.9,zh-CN;q=0.8",
}


class LaGou(Spider):
    name = "lagou_web"
    custom_settings = {
        "DOWNLOAD_DELAY": 15,
        "COOKIES_ENABLED": False,
        "DOWNLOAD_TIMEOUT": 30,
        "DOWNLOADER_MIDDLEWARES": {
            # 'zhaopin.middlewares.RandomProxyMiddleware': 100,
        },
        "ITEM_PIPELINES": {
            'zhaopin.pipelines.JobPipeline': 300,
        },
    }

    def start_requests(self):
        for kw in key_words:
            for cid, city in city_ids.items():
                url = list_url_tem.format(ct=city)
                pg = 1
                post_body = {
                    'first': "true",
                    'pn': str(pg),
                    'kd': kw + "实习"
                }
                logger.info("will crawl key word  {}".format(kw))
                yield FormRequest(url=url, callback=self.parse_list, priority=6, formdata=post_body,
                                  meta={"city": city, "kw": kw, "pg": pg}, headers=headers)

    def parse_list(self, response):
        logger.info("job list url {}".format(response.url))
        kw = response.meta["kw"]
        city = response.meta["city"]
        pg = response.meta["pg"]

        timeout_date = self.timeout_date
        timeout = False

        content = json.loads(response.body)

        for cell in content['content']["positionResult"]["result"]:
            post_item = JobShortItem()
            date = dateformatting.parse(cell["createTime"])
            if date and date < timeout_date:
                timeout = True
                logger.info("Timeout: %s < %s" % (date, timeout_date))
                break
            elif not date:
                logger.warn("parse time badly  please check dateformatting {} ".format(time_it))
                continue
            post_item["job_name"] = cell["positionName"]
            post_item["url"] = "https://www.lagou.com/jobs/{}.html".format(cell["positionId"])
            post_item["city"] = cell["city"]
            post_item["source"] = "拉勾网"
            post_item["district"] = cell["district"]
            post_item["month_salary"] = cell["salary"]
            post_item["day_salary"] = ""
            post_item["job_direction"] = key_words[kw]
            post_item["job_exp"] = cell["workYear"]
            post_item["job_edu"] = cell["education"]
            post_item["publish_man"] = cell["companyShortName"]
            post_item["publish_man_post"] = cell["companyShortName"]
            post_item["publish_time"] = dateformatting.parse(cell["createTime"]).strftime(date_format)
            post_item["company_name"] = cell["companyFullName"]
            post_item["company_addr"] = cell["district"]
            post_item["company_industry"] = cell["industryField"]
            logger.info("crawled list {} {}".format(post_item["url"], post_item["job_name"]))
            yield post_item

        if pg < 10 and not timeout:
            pg = pg + 1
            url = list_url_tem.format(ct=city)
            post_body = {
                'first': "false",
                'pn': str(pg),
                'kd': kw + "实习"
            }
            logger.info("will crawl url {}".format(url))
            yield FormRequest(url=url, callback=self.parse_list, priority=6, formdata=post_body,
                              meta={"city": city, "kw": kw, "pg": pg}, headers=headers)

    @property
    def timeout_date(self):
        return dateformatting.parse("10天前")

    @property
    def random_ip(self):
        return "201.{}.{}.{}".format(random.randrange(256), random.randrange(256), random.randrange(256))
