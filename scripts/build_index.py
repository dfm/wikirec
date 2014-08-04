#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function

import pymysql
import argparse

parser = argparse.ArgumentParser(description="Find the relevant links")
parser.add_argument("--user", "-u", help="Your MySQL user name",
                    default="root")
parser.add_argument("--password", "-p", help="Your MySQL password")
args = parser.parse_args()

with pymysql.connect(user=args.user, passwd=args.password, db="wiki",
                     charset="utf8") as c:
    c.execute("drop table if exists moviesearch")
    c.execute("""create table moviesearch (
        ms_id int unsigned NOT NULL,
        ms_title varchar(255) NOT NULL DEFAULT '',
        ms_len int unsigned NOT NULL,
        FULLTEXT(ms_title)
    ) ENGINE=MyISAM""")
    c.execute("""insert into moviesearch(ms_id,ms_title,ms_len)
    select page_id, replace(convert(page_title using utf8),'_',' '), page_len
    from movies""")
