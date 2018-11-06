# -*- coding: utf-8 -*-

import scrapy
import pymysql
import peewee
# from playhouse.shortcuts import Re

peewee.mysql = pymysql


# class MyMySQL(RetryOperationalError, peewee.MySQLDatabase):
#     pass


config = {'host': '47.104.17.60', 'password': 'uAiqwVwjJ8-i', 'port': 3306, 'user': 'root', 'charset': 'utf8mb4'}
database = peewee.MySQLDatabase('shixi', **config)


class UnknownField(object):
    def __init__(self, *_, **__):
        pass


class BaseModel(peewee.Model):
    class Meta:
        database = database


class Job(BaseModel):
    job_name = peewee.CharField()
    url = peewee.CharField(null=True)
    city = peewee.CharField(null=True)
    source = peewee.CharField(null=True)
    district = peewee.CharField(null=True)
    month_salary = peewee.CharField(null=True)
    day_salary = peewee.CharField(null=True)
    job_direction = peewee.IntegerField(null=True)
    job_exp = peewee.CharField(null=True)
    job_edu = peewee.CharField(null=True)
    publish_man = peewee.CharField(null=True)
    publish_man_post = peewee.CharField(null=True)
    publish_time = peewee.DateTimeField(null=True)
    company_name = peewee.CharField(null=True)
    company_addr = peewee.CharField(null=True)
    company_industry = peewee.CharField(null=True)
    job_industry = peewee.IntegerField(null=True)
    retain1 = peewee.IntegerField(null=True)
    retain2 = peewee.IntegerField(null=True)
    retain3 = peewee.CharField(null=True)
    retain4 = peewee.CharField(null=True)
    create_time = peewee.DateTimeField(null=True)
    update_time = peewee.DateTimeField(null=True)

    class Meta:
        db_table = 'job'
