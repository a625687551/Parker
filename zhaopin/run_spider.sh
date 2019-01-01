#!/usr/bin/env bash

ps -few | grep "scrapy crawl $1" | grep -v grep | awk '{print $2}' | xargs kill -9
nohup ~/anaconda3/bin/scrapy crawl $1  > ~/log/$1.log 2>&1 &
