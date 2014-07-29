#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function

import pymysql
import argparse

parser = argparse.ArgumentParser(description="Parse the database")
parser.add_argument("--user", "-u", help="Your MySQL user name",
                    default="root")
parser.add_argument("--password", "-p", help="Your MySQL password")
args = parser.parse_args()

blacklist = [
    "Documentary film",
    "Television film",
]

with pymysql.connect(user=args.user, passwd=args.password, db="wiki") as c:
    c.execute("drop table if exists `movies`")
    c.execute("""create table `movies` (
        `m_id` int(8) unsigned NOT NULL AUTO_INCREMENT,
        `m_title` varchar(255) NOT NULL DEFAULT '',
        `m_counter` bigint(20) unsigned NOT NULL,
        PRIMARY KEY (`m_id`),
        FULLTEXT (m_title)
    ) ENGINE=MyISAM""")

    c.execute("""insert into movies (m_id, m_title, m_counter)
    select p1.page_id, replace(convert(p1.page_title using utf8), '_', ' '),
        p1.page_counter
        from page as p0
        join pagelinks on pl_from=p0.page_id
        join page as p1 on pl_title=p1.page_title
        where p0.page_namespace=0 and p0.page_title like 'List_of_films:_%'
          and pagelinks.pl_namespace=0
          and p1.page_namespace=0
            and p1.page_title not rlike '[0-9]*_in_film.*'
            and p1.page_title not rlike '[0-9]*_film.*'
            and p1.page_title not rlike 'List_of.*'
            {0}
        group by p1.page_id
    """.format("\n".join(map("and p1.page_title not like '{0}'".format,
                             blacklist))))

    # c.execute("""
    #     select m0.m_title, count(m0.m_id) as n
    #     from movies as m0
    #     join pagelinks on pl_from=m0.m_id
    #     join page on page_title=pl_title
    #     join movies as m1 on m1.m_id=page_id
    #     where pl_namespace=0
    #     group by m0.m_id
    #     order by n DESC
    #     limit 100
    # """)
    # for _ in c.fetchall():
    #     print(_)
