# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Item
from scrapy import Field


class JobItem(Item):
    city = Field()  # 城市
    job_name = Field()  # 工作名称
    job_url = Field()  # 工作网址
    publish_time = Field()  # 发布日期
    company_name = Field()  # 公司名字
    company_industry = Field()  # 公司领域、行业
    company_stage = Field()  # 公司融资阶段
    job_welfare = Field()  # 公司福利
    job_salary = Field()  # 薪酬
    job_exp = Field()  # 工作经验要求
    job_edu = Field()  # 学历要求
    job_sec = Field()  # 工作描述
    job_tags = Field()  # 工作标签（关键词）
    job_publisher_name = Field()  # 发布人姓名
    job_publisher_post = Field()  # 发布人职位


class JobShortItem(Item):
    job_name = Field()  # 工作名称
    url = Field()  # 网址
    city = Field()  # 城市
    source = Field()  # 来源网站
    district = Field()  # 区域名字
    month_salary = Field()  # 薪酬
    day_salary = Field()  # 薪酬
    job_direction = Field()  # 工作方向
    job_exp = Field()  # 工作经验要求
    job_edu = Field()  # 学历要求
    publish_man = Field()  # 发布人姓名
    publish_man_post = Field()  # 发布人职位
    publish_time = Field()  # 发布时间 2018-10-28
    company_name = Field()  # 公司名字
    company_addr = Field()  # 公司区域
    company_industry = Field()  # 公司领域、行业
    job_industry = Field()  # 公司领域、行业
    retain1 = Field()
    retain2 = Field()
    retain3 = Field()
    retain4 = Field()
    create_time = Field()
    update_time = Field()
