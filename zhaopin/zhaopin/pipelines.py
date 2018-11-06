# -*- coding: utf-8 -*-

import scrapy
import logging
import datetime
import traceback
from .model_config import Job, database
from .items import JobShortItem

DEFAULT_CACHE_SIZE = 32

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class FieldError(Exception):
    pass


class JobPipeline(object):
    def __init__(self, cache_size=DEFAULT_CACHE_SIZE):
        self._cache = []
        self._cache_size = cache_size

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        try:
            cache_size = int(settings["JOB_CACHE_SIZE"])
        except (KeyError, ValueError, TypeError):
            cache_size = DEFAULT_CACHE_SIZE
        return cls(cache_size)

    def _check_fields(self, item):
        for field in ["job_name", "url"]:
            if field not in item:
                raise FieldError("Item has not field {}.\nItem: {}".format(field, str(item)))

    def open_spider(self, spider):
        pass

    def close_spider(self, spider):
        self._flush()

    @staticmethod
    def _set_default_value(data):
        for attr in JobShortItem.fields:
            if attr not in data:
                data[attr] = None

    def process_item(self, item, spider):
        if isinstance(item, JobShortItem):
            try:
                self._check_fields(item)
                d = dict(item)
                d.update({
                    "create_time": datetime.datetime.now(),
                    "update_time": datetime.datetime.now(),
                })
                self._set_default_value(d)
                self._cache.append(d)
                if len(self._cache) >= self._cache_size:
                    self._flush()
            except Exception:
                logger.info(traceback.format_exc())
        return item

    def _flush(self):
        if len(self._cache) == 0:
            return
        sql, params = (Job.insert_many(self._cache)).sql()
        sql += """ ON DUPLICATE KEY UPDATE
            job_name = VALUES(job_name),
            url = VALUES(url),
            city = VALUES(city),
            source = VALUES(url),
            district = IF(VALUES(district) <> "" and (district is NULL or district = ""), VALUES(district), district),
            month_salary = IF(VALUES(month_salary) <> "" and (month_salary is NULL or month_salary = ""), VALUES(month_salary), month_salary),
            day_salary = IF(VALUES(day_salary) <> "" and (day_salary is NULL or day_salary = ""), VALUES(day_salary), day_salary),
            job_direction = IF(VALUES(job_direction) <> "" and (job_direction is NULL or job_direction = ""), VALUES(job_direction), job_direction),
            job_exp = IF(VALUES(job_exp) <> "" and (job_exp is NULL or job_exp = ""), VALUES(job_exp), job_exp),
            job_edu = IF(VALUES(job_edu) <> "" and (job_edu is NULL or job_edu = ""), VALUES(job_edu), job_edu),
            publish_man = IF(VALUES(publish_man) <> "" and (publish_man is NULL or publish_man = ""), VALUES(publish_man), publish_man),
            publish_man_post = IF(VALUES(publish_man_post) <> "" and (publish_man_post is NULL or publish_man_post = ""), VALUES(publish_man_post), publish_man_post),
            publish_time =VALUES(publish_time),
            company_name = IF(VALUES(company_name) <> "" and (company_name is NULL or company_name = ""), VALUES(company_name), company_name),
            company_addr = IF(VALUES(company_addr) <> "" and (company_addr is NULL or company_addr = ""), VALUES(company_addr), company_addr),
            company_industry = IF(VALUES(company_industry) <> "" and (company_industry is NULL or company_industry = ""), VALUES(company_industry), company_industry),
            job_industry = IF(VALUES(job_industry) <> "" and (job_industry is NULL or job_industry = ""), VALUES(job_industry), job_industry),
            retain1 = IF(VALUES(retain1) <> "" and (retain1 is NULL or retain1 = ""), VALUES(retain1), retain1),
            retain2 = IF(VALUES(retain2) <> "" and (retain2 is NULL or retain2 = ""), VALUES(retain2), retain2),
            retain3 = IF(VALUES(retain3) <> "" and (retain3 is NULL or retain3 = ""), VALUES(retain3), retain3),
            retain4 = IF(VALUES(retain4) <> "" and (retain4 is NULL or retain4 = ""), VALUES(retain4), retain4),
            create_time = VALUES(create_time),
            update_time = VALUES(update_time) """
        try:
            logger.debug("Job Sql is %s, %s" % (sql, params))
            length = len(self._cache)
            database.execute_sql(sql, params)
            logger.info("Uploaded %d items to Job." % length)
        except:
            logger.error(traceback.format_exc())
        finally:
            self._cache = []
