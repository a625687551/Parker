#!/usr/bin/env bash

ps -few | grep "srcapy crawl $1" | grep -v grep | awk '{print $2}' | xargs kill -9
nohup srcapy crawl $1  > ~/log/$1.log 2>&1 &