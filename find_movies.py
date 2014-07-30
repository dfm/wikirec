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
    "Documentary_film",
    "Television_film",
]

with pymysql.connect(user=args.user, passwd=args.password, db="wiki") as c:
    # Set up the table.
    print("Setting up the table")
    c.execute("drop table if exists `movies`")
    c.execute("""create table `movies` (
        `m_id` int(8) unsigned NOT NULL AUTO_INCREMENT,
        `m_title` varchar(255) NOT NULL DEFAULT '',
        `m_counter` bigint(20) unsigned NOT NULL,
        `m_len` int(10) unsigned,
        PRIMARY KEY (`m_id`),
        FULLTEXT (m_title)
    ) ENGINE=MyISAM""")

    # Find all the pages linked to from lists of movies.
    print("Searching lists of movies")
    c.execute("""insert into movies (m_id, m_title, m_counter, m_len)
    select p1.page_id, replace(convert(p1.page_title using utf8), '_', ' '),
        p1.page_counter, p1.page_len
        from page as p0
        join pagelinks on pl_from=p0.page_id
        join page as p1 on pl_title=p1.page_title
        where p0.page_namespace=0 and p0.page_is_redirect=0
            and p0.page_title like 'List_of_films:_%'
          and pagelinks.pl_namespace=0
          and p1.page_namespace=0 and p1.page_is_redirect=0
            and p1.page_title not rlike '^[0-9]*_in_film.*'
            and p1.page_title not rlike '^[0-9]*_film.*'
            and p1.page_title not rlike '^List_of.*'
            {0}
        group by p1.page_id
    """.format("\n".join(map("and p1.page_title not like '{0}'".format,
                             blacklist))))

    # Search for pages ending in something like (film) or (2014 film).
    print("Searching for 'orphan' movies")
    c.execute(r"""insert ignore into movies (m_id, m_title, m_counter, m_len)
    select page_id, replace(convert(page_title using utf8), '_', ' '),
        page_counter, page_len
    from page
    where
        page_namespace=0 and page_is_redirect=0
        and page_title rlike '\\([0-9]*_*film\\)'
    """)

    c.execute(r"create index m_len on movies (m_len ASC)")

    c.execute("select count(*) from movies")
    n = int(c.fetchone()[0])
    print("Found {0} movies".format(n))
