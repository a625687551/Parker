# coding:utf-8
import logging
import random
import json

from urllib.parse import quote_plus

from scrapy import Spider
from scrapy import FormRequest

from zhaopin.items import JobShortItem

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)
date_format = '%Y-%m-%d %H:%M:%S'

city_ids = {101010100: "北京",
            101010101: "上海",
            # 101010102: "西安",
            101010103: "杭州",
            101010104: "深圳",
            101010105: "广州"}
# key_words = ["数据分析", "数据挖掘", "数据建模", "机器学习"]
key_words = {"java": 1, "python": 4, "C++": 2, "数据挖掘": 6, "android": 7,
             "ios": 8, "测试": 10, "web": 3, "运维": 9, "php": 5}
# city_ids = {101010100: u"北京"}
# key_words = ["数据分析"]
# list_url_tem = "https://www.lagou.com/jobs/positionAjax.json?px=default&city={ct}&needAddtionalResult=false"
list_url_tem = "https://www.lagou.com/jobs/positionAjax.json?needAddtionalResult=true"
detail_url = "https://www.lagou.com/jobs/{}.html"


def random_ip():
    return "201.{}.{}.{}".format(random.randrange(256), random.randrange(256), random.randrange(256))


headers = {
    "Host": "www.lagou.com",
    "Connection": "Keep-alive",
    "Origin": "https://www.lagou.com",
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Referer": "https://www.lagou.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome Safari/537.36",
}


class LaGou(Spider):
    name = "lagou_web"
    custom_settings = {
        "DOWNLOAD_DELAY": 3,
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
        for kw in key_words:
            kw = kw + "实习"
            for cid, name in city_ids.items():
                url = list_url_tem.format(ct=name)
                pg = 1
                post_body = {
                    'first': "true",
                    'pn': str(pg),
                    'kd': kw
                }
                # post_body = post_body.format(pg=1, kw=quote_plus(kw))
                logger.info("will crawl url {}".format(url))
                yield FormRequest(url=url, callback=self.parse_list, priority=6, formdata=post_body,
                                  meta={"city": name, "kw": kw, "pg": pg}, headers=headers)

    def parse_list(self, response):
        logger.info("job list url {}".format(response.url))
        kw = response.meta["kw"]
        city = response.meta["city"]
        pg = response.meta["pg"]

        content = json.loads(response.body)

        for cell in content['content']["positionResult"]["result"]:
            post_item = JobShortItem()
            post_item["job_name"] = cell["positionName"]
            post_item["url"] = "https://www.lagou.com/jobs/{}.html".format(cell["positionId"])
            post_item["city"] = cell["city"]
            post_item["source"] = "拉勾网"
            post_item["district"] = cell["district"]
            post_item["month_salary"] = cell["salary"]
            post_item["day_salary"] = ""
            post_item["job_direction"] = ""
            post_item["job_exp"] = cell["workYear"]
            post_item["job_edu"] = cell["education"]
            post_item["publish_man"] = cell["companyShortName"]
            post_item["publish_man_post"] = cell["companyShortName"]
            post_item["publish_time"] = cell["createTime"]
            post_item["company_name"] = cell["companyFullName"]
            post_item["company_addr"] = cell["district"]
            post_item["company_industry"] = cell["industryField"]

        if pg < 30:
            pg = pg + 1
            url = list_url_tem.format(ct=city)
            post_body = {
                'first': "false",
                'pn': str(pg),
                'kd': kw
            }
            logger.info("will crawl url {}".format(url))
            yield FormRequest(url=url, callback=self.parse_list, priority=6, formdata=post_body,
                              meta={"city": city, "kw": kw, "pg": pg}, headers=headers)


